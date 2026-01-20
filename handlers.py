import json
from bson import ObjectId
from datetime import date, datetime
from slack_sdk.errors import SlackApiError
from models.reminder import Reminder, ReminderStatus
from blocks.reminder import *
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

        error_messages = []
        today = date.today()

        # 입력한 값 검증
        if start_date >= end_date:
            error_messages.append("시작일은 종료일보다 이전이어야 해요")

        if end_date < today:
            error_messages.append("종료일은 오늘 이후로 선택해주세요")

        # 검증 실패 시 함수 종료
        if error_messages:
            self.client.chat_postMessage(
                channel=admin_slack_id,
                text="리마인드 생성 오류 발생",
                blocks=reminder_error_message_block(error_messages)
            )
            return

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
                text="리마인드 삭제 오류",
                blocks=[
                    get_mrkdwn_block(":dotted_line_face: 삭제할 리마인드가 없어요"),
                    get_context_block([
                        {
                            "type": "mrkdwn",
                            "text": "️:warning: 진행 예정이거나 진행 중인 리마인드만 삭제할 수 있어요"
                        }
                    ])
                ]
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

    def send_reminder_message(self):
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
                    blocks=remind_alarm_message_block(consts=reminder.consts, selected_users_slack_key=alarm_user_list, reminder_id=str(reminder.id))
                )

                reminder.last_triggered_at = today
                if today >= reminder.end_date.date():
                    # reminder.status = ReminderStatus.DONE

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

    def confirm_reminder(self, body):
        user_slack_id = body.get("user", {}).get("id", "")
        reminder_id = body.get("actions", [])[0].get("value", "")

        reminder = Reminder.objects(id=ObjectId(reminder_id), status__in=["PENDING", "ACTIVE"]).first()

        if not reminder:
            return

        old_completed_users = reminder.completed_users
        remain_users = list(set(reminder.selected_users) - set(old_completed_users))

        if user_slack_id not in remain_users:
            return

        old_completed_users.append(user_slack_id)
        reminder.completed_users = old_completed_users

        if len(remain_users) == 1:
            self.client.chat_postMessage(
                channel=reminder.channel_id,
                thread_ts=reminder.message_ts,
                text="모든 담당자 작업 완료",
                blocks=remind_complete_message_block()
            )
            reminder.status = ReminderStatus.DONE

        reminder.save()

        self.client.chat_postEphemeral(
            channel=reminder.channel_id,
            thread_ts=reminder.message_ts,
            user=user_slack_id,
            text="작업 완료",
            blocks=[
                get_mrkdwn_block("작업이 완료되었어요 고생하셨어요! :raised_hands::skin-tone-2:"),
            ]
        )

    def open_progress_reminder_shortcut(self, body):
        channel_id = body.get("channel", {}).get("id", "")
        message_ts = body.get("message", {}).get("ts", "")

        reminder = Reminder.objects(channel_id=channel_id, message_ts=message_ts).order_by("-created_at").first()

        if not reminder:
            return

        self.client.views_open(
            trigger_id=body.get("trigger_id"),
            view=reminder_progress_modal_view(consts=reminder.consts, selected_users=reminder.selected_users, completed_users=reminder.completed_users)
        )