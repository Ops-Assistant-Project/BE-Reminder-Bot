import json
from handlers import ReminderHandler


# @slack_app.shortcut("CREATE_REMINDER")
def open_create_reminder_shortcut(ack, body, client):
    ack()

    handlers = ReminderHandler(client=client)
    return handlers.open_create_reminder_shortcut(body)

# @slack_app.view("reminder_create_submit")
def create_reminder(ack, body, client):
    ack()

    handlers = ReminderHandler(client=client)
    return handlers.create_reminder(body)