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

# @slack_app.shortcut("DELETE_REMINDER")
def open_delete_reminder_shortcut(ack, body, client):
    ack()

    handlers = ReminderHandler(client=client)
    return handlers.open_delete_reminder_shortcut(body)

# @slack_app.view("reminder_delete_submit")
def delete_reminder(ack, body, client):
    ack()

    handlers = ReminderHandler(client=client)
    return handlers.delete_reminder(body)

# @slack_app.action("remind_confirm")
def confirm_reminder(ack, body, client):
    ack()

    handlers = ReminderHandler(client=client)
    return handlers.confirm_reminder(body)

def open_progress_reminder_shortcut(ack, body, client):
    ack()

    handlers = ReminderHandler(client=client)
    return handlers.open_progress_reminder_shortcut(body)