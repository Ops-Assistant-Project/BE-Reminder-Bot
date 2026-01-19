from fastapi import APIRouter, Request
from slack_bolt.adapter.fastapi import SlackRequestHandler
from modules.slack import BoltApp
from common.slack import SlackBotName
from services import (open_create_reminder_shortcut, create_reminder,
                      open_delete_reminder_shortcut, delete_reminder,
                      send_reminder_message, confirm_reminder)

router = APIRouter(prefix="/slack", tags=["Slack"])

slack_app = BoltApp(SlackBotName.REMINDER_BOT)
handler = SlackRequestHandler(slack_app)

slack_app.shortcut("CREATE_REMINDER")(open_create_reminder_shortcut)
slack_app.view("reminder_create_submit")(create_reminder)
slack_app.shortcut("DELETE_REMINDER")(open_delete_reminder_shortcut)
slack_app.view("reminder_delete_submit")(delete_reminder)
slack_app.command("/test_reminder")(send_reminder_message)  # 리마인드 알림 테스트용
slack_app.action("remind_confirm")(confirm_reminder)


@router.post("/events")
async def slack_events(req: Request):
    return await handler.handle(req)
