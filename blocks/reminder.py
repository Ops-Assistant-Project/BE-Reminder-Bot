import json


def create_reminder_modal_view(channel_id: str, message_ts: str):
    return {
        "type": "modal",
        "callback_id": "reminder_create_submit",
        "private_metadata": json.dumps({
            "channel_id": channel_id,
            "message_ts": message_ts
        }),
        "title": {
            "type": "plain_text",
            "text": "리마인드 생성",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "users_block",
                "element": {
                    "type": "multi_users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "담당자를 선택하세요",
                        "emoji": True
                    },
                    "action_id": "users_select_action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "담당자 선택",
                    "emoji": True
                },
                "optional": False
            },
            {
                "type": "input",
                "block_id": "start_date_block",
                "label": {
                    "type": "plain_text",
                    "text": "시작일"
                },
                "element": {
                    "type": "datepicker",
                    "action_id": "start_date",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "시작 날짜 선택"
                    }
                }
            },
            {
                "type": "input",
                "block_id": "end_date_block",
                "label": {
                    "type": "plain_text",
                    "text": "종료일"
                },
                "element": {
                    "type": "datepicker",
                    "action_id": "end_date",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "종료 날짜 선택"
                    }
                }
            },
            {
                "type": "input",
                "block_id": "text_block",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "input_text_action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "리마인드 문구",
                    "emoji": True
                },
                "optional": False
            }
        ]
    }