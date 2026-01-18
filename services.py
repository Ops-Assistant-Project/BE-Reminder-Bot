import json
from slack_sdk.errors import SlackApiError
from common.slack_blocks import get_mrkdwn_block
from blocks.reminder import create_reminder_modal_view


# @slack_app.shortcut("CREATE_REMINDER")
def open_create_reminder_shortcut(ack, body, client):
    ack()

    channel_id = body.get("channel", {}).get("id", "")
    message_ts = body.get("message", {}).get("ts", "")

    client.views_open(
        trigger_id=body.get("trigger_id"),
        view=create_reminder_modal_view(channel_id, message_ts)
    )

# @slack_app.view("reminder_create_submit")
def create_reminder(ack, body, client):
    ack()

    admin_slack_key = body.get('user', {}).get('id', '') # 생성한 사람 slack_key

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
