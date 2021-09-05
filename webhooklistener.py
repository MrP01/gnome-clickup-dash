import os

import motor.motor_asyncio
from fastapi import FastAPI

from models import *

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client["completed-tasks"]


@app.post("/handle-task-status-update")
async def handleTaskStatusUpdate(update: WebhookUpdate):
    print(update)
    if update.event == "taskStatusUpdated":
        for historyItem in update.history_items:
            if historyItem.after["type"] == "closed":
                await db.completedTasks.insert_one(CompletedTaskLog(
                    timestamp=historyItem.get_datetime(),
                    task_id=update.task_id,
                    task_name="Todo",
                    effort=1
                ))
            else:
                print("The status is not closed. Ignoring :)", historyItem.after)
    else:
        print("This is not what we are looking for.")
    return {"message": "thanks!"}  # what we send back to Clickup is not relevant


@app.get("/get-completed")
async def getCompletedTasks(start: datetime.datetime, to: datetime.datetime):
    return await db.completedTasks.find({
        "timestamp": {"$gte": start, "$lt": to}
    })
