from fastapi import FastAPI
from db.mongodb import connect_to_mongo
from controllers import router as ReminderRouter

app = FastAPI(title="Reminder Bot API")

@app.on_event("startup")
def startup():
    connect_to_mongo()

@app.get("/")
def root():
    return {"message": "Hello World"}

app.include_router(ReminderRouter, tags=["Reminder"])