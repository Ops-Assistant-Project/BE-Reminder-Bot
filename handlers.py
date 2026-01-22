from bson import ObjectId
from models.reminder import Reminder, ReminderStatus
from blocks.reminder import *
from common.slack.call import slack_call, slack_call_safe
from common.slack.blocks import get_mrkdwn_block, get_header_block, get_divider_block, get_context_block


class ReminderHandler():
    def __init__(self, client):
        self.client = client

    def open_create_reminder_shortcut(self, body):
        channel_id = body.get("channel", {}).get("id", "")
        message_ts = body.get("message", {}).get("ts", "")

        slack_call(
            self.client.views_open,
            action="open_create_reminder_shortcut",
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

        is_reminder = Reminder.objects(channel_id=channel_id, message_ts=message_ts, status__in=["PENDING", "ACTIVE"]).first()
        if is_reminder:
            error_messages.append("이미 리마인드가 존재하는 채팅이에요 삭제 후 생성해주세요")

        # 검증 실패 시 함수 종료
        if error_messages:
            slack_call_safe(
                self.client.chat_postMessage,
                action="reminder_create_validation_error",
                channel=admin_slack_id,
                text="리마인드 생성 오류 발생",
                blocks=reminder_error_message_block(error_messages),
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
            try:
                res = slack_call(
                    self.client.users_info,
                    action="get_user_info",
                    user=user,
                )
                users_name.append(res.get("user", {}).get("real_name", f"<@{user}>"))
            except Exception:
                users_name.append(f"<@{user}>")

        # 스레드에 생성 완료 메시지 추가
        slack_call(
            self.client.chat_postMessage,
            action="reminder_create_success_message",
            channel=channel_id,
            text="리마인드 생성 완료",
            thread_ts=message_ts,
            blocks=remind_start_message_block(
                consts=consts,
                start_date=start_date,
                end_date=end_date,
                selected_users_name=users_name,
            ),
        )

    def open_delete_reminder_shortcut(self, body):
        channel_id = body.get("channel", {}).get("id", "")
        message_ts = body.get("message", {}).get("ts", "")

        slack_call(
            self.client.views_open,
            action="open_delete_reminder_modal",
            trigger_id=body.get("trigger_id"),
            view=delete_reminder_modal_view(channel_id, message_ts),
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
            slack_call_safe(
                self.client.chat_postEphemeral,
                action="delete_reminder_not_found",
                channel=channel_id,
                thread_ts=message_ts,
                user=body.get('user', {}).get('id', ''),
                text="리마인드 삭제 오류",
                blocks=[
                    get_mrkdwn_block(":dotted_line_face: 삭제할 리마인드가 없어요"),
                    get_context_block([
                        {
                            "type": "mrkdwn",
                            "text": ":warning: 진행 예정이거나 진행 중인 리마인드만 삭제할 수 있어요"
                        }
                    ])
                ]
            )
            return

        remind.status = ReminderStatus.DONE
        remind.save()

        slack_call(
            self.client.chat_postMessage,
            action="delete_reminder_success",
            channel=channel_id,
            text="리마인드 삭제 완료",
            thread_ts=message_ts,
            blocks=[
                get_header_block(":wastebasket: 리마인드가 삭제됐어요"),
                get_divider_block(),
                get_mrkdwn_block(f"```{remind.consts}```"),
                get_context_block([
                    {
                        "type": "mrkdwn",
                        "text": ":no_entry: 리마인드가 삭제되어 더 이상 알림이 가지 않아요"
                    }
                ])
            ]
        )

    def confirm_reminder(self, body):
        user_slack_id = body.get("user", {}).get("id", "")
        reminder_id = body.get("actions", [])[0].get("value", "")

        reminder = Reminder.objects(id=ObjectId(reminder_id), status__in=["PENDING", "ACTIVE"]).first()

        if not reminder:
            return

        old_completed_users = reminder.completed_users
        remain_users = list(set(reminder.selected_users) - set(old_completed_users))

        if user_slack_id in old_completed_users:
            slack_call_safe(
                self.client.chat_postEphemeral,
                action="confirm_reminder_already_done",
                channel=reminder.channel_id,
                thread_ts=reminder.message_ts,
                user=user_slack_id,
                text="작업 완료",
                blocks=[get_mrkdwn_block("이미 작업을 완료했어요! :heart_hands::skin-tone-2:")]
            )
            return

        if user_slack_id not in remain_users:
            return

        old_completed_users.append(user_slack_id)
        reminder.completed_users = old_completed_users

        if len(remain_users) == 1:
            slack_call(
                self.client.chat_postMessage,
                action="confirm_reminder_all_done",
                channel=reminder.channel_id,
                thread_ts=reminder.message_ts,
                text="모든 담당자 작업 완료",
                blocks=remind_complete_message_block()
            )
            reminder.status = ReminderStatus.DONE

        reminder.save()

        # 기존 메시지에서 완료한 담당자 언급 제외
        history = slack_call(
            self.client.conversations_replies,
            action="fetch_reminder_thread",
            channel=reminder.channel_id,
            ts=reminder.message_ts
        )

        messages = history.get("messages", [])
        for message in messages:
            if message.get("text") == "리마인드 알림 도착":
                message_blocks = message.get("blocks", [])
                message_reminder_id = message_blocks[-1].get("accessory", {}).get("value")

                if reminder_id == message_reminder_id:
                    user_info = slack_call_safe(
                        self.client.users_info,
                        action="fetch_user_info_for_strike",
                        user=user_slack_id
                    )

                    if not user_info:
                        return

                    text = message_blocks[3].get("text", {}).get("text", "")
                    text = text.replace(f"<@{user_slack_id}>", f"~{user_info.get('user', {}).get('real_name', '')}~")

                    message_blocks[3]["text"]["text"] = text

                    slack_call(
                        self.client.chat_update,
                        action="update_reminder_message",
                        channel=reminder.channel_id,
                        ts=message.get("ts"),
                        text="리마인드 알림 도착",
                        blocks=message_blocks
                    )

        # 작업 완료 비밀 메시지 전송
        slack_call_safe(
            self.client.chat_postEphemeral,
            action="confirm_reminder_done_ephemeral",
            channel=reminder.channel_id,
            thread_ts=reminder.message_ts,
            user=user_slack_id,
            text="작업 완료",
            blocks=[get_mrkdwn_block("작업이 완료되었어요 고생하셨어요! :raised_hands::skin-tone-2:")]
        )


    def open_progress_reminder_shortcut(self, body):
        channel_id = body.get("channel", {}).get("id", "")
        message_ts = body.get("message", {}).get("ts", "")

        reminder = Reminder.objects(channel_id=channel_id, message_ts=message_ts).order_by("-created_at").first()

        if not reminder:
            return

        slack_call(
            self.client.views_open,
            action="open_reminder_progress_modal",
            trigger_id=body.get("trigger_id"),
            view=reminder_progress_modal_view(
                consts=reminder.consts,
                selected_users=reminder.selected_users,
                completed_users=reminder.completed_users,
            ),
        )

    @staticmethod
    def _calculate_reminder_status(
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