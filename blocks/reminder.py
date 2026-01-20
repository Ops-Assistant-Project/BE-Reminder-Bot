import json
from datetime import date


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
                        "text": "시작일 선택"
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
                        "text": "종료일 선택"
                    }
                }
            },
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

def remind_start_message_block(consts: str, selected_users_name: list, start_date: date, end_date: date):
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":wave::skin-tone-2: 리마인드가 생성되었어요",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{consts}```"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*담당자*: {', '.join(selected_users_name)}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*리마인드 기간*: {start_date} ~ {end_date}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "⚠️ 리마인드 기간동안 매일 오전 10시에 담당자를 언급해요"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "⚠️ 작업을 완료한 담당자는 리마인드에서 제외돼요"
                }
            ]
        }
    ]

def remind_alarm_message_block(consts: str, selected_users_slack_key: list, reminder_id: str):
    return [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": ":bell: 리마인드가 도착했어요",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"```{consts}```"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": " ".join(f"<@{slack_key}>" for slack_key in selected_users_slack_key)
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "작업을 완료했으면 버튼을 클릭해주세요 :point_right::skin-tone-2:"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "작업 완료",
					"emoji": True
				},
				"style": "primary",
				"action_id": "remind_confirm",
                "value": reminder_id
			}
		}
	]

def remind_complete_message_block():
    return [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": ":tada: 작업이 완료됐어요",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*모든 담당자가 작업을 완료했어요.*\n리마인드는 여기서 종료됩니다 🙌"
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": ":man-bowing::skin-tone-2: 필요하면 언제든 새로운 리마인드를 만들어주세요"
				}
			]
		}
	]

def remind_end_message_block():
    return [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "📌 리마인드가 종료됐어요",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "설정된 *리마인드 기간이 종료* 되어 알림이 중단됐어요\n필요하다면 새로운 리마인드를 다시 생성해주세요."
			}
		}
	]

def delete_reminder_modal_view(channel_id: str, message_ts: str):
    return {
        "type": "modal",
        "callback_id": "reminder_delete_submit",
        "private_metadata": json.dumps({
            "channel_id": channel_id,
            "message_ts": message_ts
        }),
        "title": {
            "type": "plain_text",
            "text": "⚠️ 리마인드 삭제",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "삭제"
        },
        "close": {
            "type": "plain_text",
            "text": "취소"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*정말로 이 리마인드를 삭제할까요?*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "삭제하면 해당 리마인드는 즉시 종료되며,\n담당자에게 더 이상 알림이 전송되지 않아요"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "❗ *이 작업은 되돌릴 수 없어요*"
                    }
                ]
            }
        ]
    }

def reminder_error_message_block(error_messages: list):
    msg = '\n'.join(error_messages)
    return [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "⚠️ 리마인드 생성 중 문제가 발생했어요",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "입력하신 정보 중 확인이 필요한 항목이 있어요 \n아래 내용을 확인하고 다시 시도해주세요 🙏"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"```{msg}```"
			}
		}
	]