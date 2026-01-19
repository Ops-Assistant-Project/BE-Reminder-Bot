from enum import Enum
from mongoengine import (
    Document,
    StringField,
    DateTimeField
)
from mongoengine.fields import EnumField, ListField

class ReminderStatus(str, Enum):
    PENDING = "PENDING" # 시작 전
    ACTIVE = "ACTIVE"   # 진행 중
    DONE = "DONE"   # 완료

class Reminder(Document):
    meta = {"collection": "reminders"}

    admin_slack_id = StringField()
    selected_users = ListField(StringField())
    completed_users = ListField(StringField())
    start_date = DateTimeField()
    end_date = DateTimeField()
    last_triggered_at = DateTimeField()
    consts = StringField()
    status = EnumField(ReminderStatus, default=ReminderStatus.PENDING)

    channel_id = StringField()
    message_ts = StringField()

