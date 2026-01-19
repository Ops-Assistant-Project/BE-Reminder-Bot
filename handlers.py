import json
from datetime import date, datetime, timezone, timedelta
from slack_sdk.errors import SlackApiError
from models.reminder import Reminder, ReminderStatus
from blocks.reminder import create_reminder_modal_view, remind_start_message_block, delete_reminder_modal_view, remind_alarm_message_block
from common.slack_blocks import get_mrkdwn_block, get_header_block, get_divider_block, get_context_block

class ReminderHandler():
    def __init__(self, client):
        self.client = client

    def open_create_reminder_shortcut(self, body):
        channel_id = body.get("channel", {}).get("id", "")
        message_ts = body.get("message", {}).get("ts", "")

        self.client.views_open(
            trigger_id=body.get("trigger_id"),
            view=create_reminder_modal_view(channel_id, message_ts)
        )

    def create_reminder(self, body):
        admin_slack_id = body.get('user', {}).get('id', '') # 생성한 사람 slack_key

        # 입력한 값
        values = body.get('view', {}).get('state', {}).get('values', {})
        selected_users = values.get('users_block', {}).get('users_select_action', {}).get('selected_users', [])
        start_date = values.get('start_date_block', {}).get('start_date', {}).get('selected_date', '')
        end_date = values.get('end_date_block', {}).get('end_date', {}).get('selected_date', '')
        consts = values.get('text_block', {}).get('input_text_action', {}).get('value', '')

        # 메타데이터
        metadata = json.loads(body.get('view', {}).get("private_metadata"))
        channel_id = metadata.get("channel_id", "")
        message_ts = metadata.get("message_ts", {})

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_date >= end_date:
            return self.client.chat_postMessage(
                channel=admin_slack_id,
                text="리마인드 생성 오류 발생",
                blocks=[get_header_block(":warning: 리마인드 생성 오류가 발생했어요")]
            )

        # DB 저장
        remind = Reminder(
            admin_slack_id=admin_slack_id,
            selected_users=selected_users,
            start_date=start_date,
            end_date=end_date,
            consts=consts,
            channel_id=channel_id,
            message_ts=message_ts,
            status=self._calculate_reminder_status(start_date=start_date, end_date=end_date)
        )
        remind.save()

        users_name = []
        for user in selected_users:
            u = self.client.users_info(user=user)
            users_name.append(u.get('user', {}).get('real_name', ''))

        # 스레드에 생성 완료 메시지 추가
        self.client.chat_postMessage(
            channel=channel_id,
            text="리마인드 생성 완료",
            thread_ts=message_ts,
            blocks=remind_start_message_block(consts=consts, start_date=start_date, end_date=end_date, selected_users_name=users_name)
        )

    def _calculate_reminder_status(
            self,
            start_date: date,
            end_date: date,
            today: date | None = None,
    ) -> ReminderStatus:
        if today is None:
            today = date.today()

        if today < start_date:
            return ReminderStatus.PENDING

        if start_date <= today <= end_date:
            return ReminderStatus.ACTIVE

        return ReminderStatus.DONE

    def open_delete_reminder_shortcut(self, body):
        channel_id = body.get("channel", {}).get("id", "")
        message_ts = body.get("message", {}).get("ts", "")

        self.client.views_open(
            trigger_id=body.get("trigger_id"),
            view=delete_reminder_modal_view(channel_id, message_ts)
        )

    def delete_reminder(self, body):
        metadata = json.loads(body.get("view", {}).get("private_metadata", ''))
        channel_id = metadata.get("channel_id", "")
        message_ts = metadata.get("message_ts", "")

        remind = Reminder.objects(
            channel_id=channel_id,
            message_ts=message_ts,
            status__in=["PENDING", "ACTIVE"]
        ).first()

        if not remind:
            self.client.chat_postEphemeral(
                channel=channel_id,
                thread_ts=message_ts,
                user=body.get('user', {}).get('id', ''),
                blocks=[get_mrkdwn_block(":dotted_line_face: 삭제할 리마인드가 없어요")]
            )
            return

        remind.status = ReminderStatus.DONE
        remind.save()

        self.client.chat_postMessage(
            channel=channel_id,
            text="리마인드 삭제 완료",
            thread_ts=message_ts,
            blocks=[
                get_header_block(f":wastebasket: 리마인드가 삭제됐어요"),
                get_divider_block(),
                get_mrkdwn_block(f"```{remind.consts}```"),
                get_context_block([
                    {
                        "type": "mrkdwn",
                        "text": "️:no_entry: 리마인드가 삭제되어 더 이상 알림이 가지 않아요"
                    }
                ])
            ]
        )

    def send_reminder_message(self, body):
        today = datetime.now().date()
        reminders = Reminder.objects(status__in=["PENDING", "ACTIVE"])

        for reminder in reminders:
            if reminder.start_date.date() <= today <= reminder.end_date.date():
                alarm_user_list = list(set(reminder.selected_users) - set(reminder.completed_users))
                # 알림 전송
                self.client.chat_postMessage(
                    channel=reminder.channel_id,
                    text="리마인드 알림 도착",
                    thread_ts=reminder.message_ts,
                    blocks=remind_alarm_message_block(consts=reminder.consts, selected_users_slack_key=alarm_user_list)
                )

                reminder.last_triggered_at = today
                if today >= reminder.end_date.date():
                    reminder.status = ReminderStatus.DONE

                    # 종료 예정 메시지 전송
                    self.client.chat_postMessage(
                        channel=reminder.channel_id,
                        text="리마인드 종료 예정",
                        thread_ts=reminder.message_ts,
                        blocks=[get_context_block([
                            {
                                "type": "mrkdwn",
                                "text": ":bulb: 오늘이 리마인드 마지막 날이에요"
                            },
                            {
                                "type": "mrkdwn",
                                "text": ":bulb: 아직 작업을 완료하지 못한 담당자분들은 작업 완료를 눌러주세요"
                            }])
                        ])

                reminder.save()

    @staticmethod
    def _get_today_kst():
        return (datetime.now(timezone.utc) + timedelta(hours=9))

    def confirm_reminder(self, body):
        print(body)