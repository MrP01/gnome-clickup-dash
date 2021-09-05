import os

import motor.motor_asyncio
import requests
from fastapi import FastAPI, Depends
from starlette.requests import Request

from models import *

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client["completed-tasks"]


@app.post("/handle-task-status-update")
async def handleTaskStatusUpdate(update: WebhookUpdate):
    print(update)
    if update.event == "taskStatusUpdated":
        for historyItem in update.history_items:
            user = User.parse_obj(await db.users.find_one({"clickup_email": historyItem.user["email"]}))
            if user is None:
                print("Couldn't find the associated user.")
                return {"message": "could not find user :("}
            if historyItem.after["type"] == "closed":
                response = requests.get(f"https://api.clickup.com/api/v2/task/{update.task_id}/", headers={"Authorization": user.clickup_api_token})
                assert response.ok
                taskDetail = response.json()
                task = CompletedTaskLog(
                    timestamp=historyItem.get_datetime(),
                    task_id=update.task_id,
                    task_name=taskDetail["name"],
                    username=user.username
                )
                try:
                    effortField = [cf for cf in taskDetail["custom_fields"] if cf["name"] == "Effort"][0]
                    task.points = float(effortField["type_config"]["options"][effortField["value"]]["name"])
                except (KeyError, ValueError):
                    print("Effort field could not be parsed.")
                await db.completedTasks.insert_one(task.dict())
            else:
                print("The status is not closed. Ignoring :)", historyItem.after)
    else:
        print("This is not what we are looking for.", update.event)
    return {"message": "thanks!"}  # what we send back to Clickup is not relevant


async def get_current_user(request: Request) -> User:
    user = await db.users.find_one({"auth_token": request.headers["Authorization"]})
    return User.parse_obj(user)


@app.get("/get-completed")
async def getCompletedTasks(start: datetime.datetime, to: datetime.datetime, user: User = Depends(get_current_user)) -> list:
    return await db.completedTasks.find({
        "timestamp": {"$gte": start, "$lt": to},
        "username": user.username
    })
