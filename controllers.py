from fastapi import APIRouter, Request
from slack_bolt.adapter.fastapi import SlackRequestHandler
from modules.slack import BoltApp
from common.slack import SlackBotName
from services import (open_create_reminder_shortcut, create_reminder,
                      open_delete_reminder_shortcut, delete_reminder)

router = APIRouter(prefix="/slack", tags=["Slack"])

slack_app = BoltApp(SlackBotName.REMINDER_BOT)
handler = SlackRequestHandler(slack_app)

slack_app.shortcut("CREATE_REMINDER")(open_create_reminder_shortcut)
slack_app.view("reminder_create_submit")(create_reminder)
slack_app.shortcut("DELETE_REMINDER")(open_delete_reminder_shortcut)
slack_app.view("reminder_delete_submit")(delete_reminder)


@router.post("/events")
async def slack_events(req: Request):
    return await handler.handle(req)
