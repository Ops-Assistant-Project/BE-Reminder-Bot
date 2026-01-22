from datetime import datetime
from common.crypto import decrypt
from common.slack import SlackEnvKey, SlackBotName
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from models.reminder import Reminder, ReminderStatus
from blocks.reminder import remind_alarm_message_block, remind_end_message_block
from common.slack_blocks import get_context_block


def send_reminder_message():
    today = datetime.now().date()
    client = WebClient(token=decrypt(SlackEnvKey.BOT_TOKENS.get(SlackBotName.REMINDER_BOT)))
    reminders = Reminder.objects(status__in=["PENDING", "ACTIVE"])

    for reminder in reminders:
        if reminder.start_date.date() <= today <= reminder.end_date.date():
            alarm_user_list = list(set(reminder.selected_users) - set(reminder.completed_users))
            # 알림 전송
            client.chat_postMessage(
                channel=reminder.channel_id,
                text="리마인드 알림 도착",
                thread_ts=reminder.message_ts,
                blocks=remind_alarm_message_block(consts=reminder.consts, selected_users_slack_key=alarm_user_list,
                                                  reminder_id=str(reminder.id))
            )

            reminder.last_triggered_at = today
            if today >= reminder.end_date.date():
                # 종료 예정 메시지 전송
                client.chat_postMessage(
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
        else:
            client.chat_postMessage(
                channel=reminder.channel_id,
                text="리마인드 종료",
                thread_ts=reminder.message_ts,
                blocks=remind_end_message_block()
            )
            reminder.status = ReminderStatus.DONE

            reminder.save()

    return