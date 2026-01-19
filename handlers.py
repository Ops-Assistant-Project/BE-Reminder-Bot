import json
from datetime import date, datetime
from slack_sdk.errors import SlackApiError
from models.reminder import Reminder, ReminderStatus
from blocks.reminder import create_reminder_modal_view, remind_start_message_block, delete_reminder_modal_view
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