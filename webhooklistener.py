import os
from typing import List, Optional

import motor.motor_asyncio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URL"])


class HistoryItemData(BaseModel):
    status_type: str


class HistoryItem(BaseModel):
    id: str
    type: int
    date: str
    field: str
    parent_id: str
    data: HistoryItemData
    source: Optional[str]
    user: dict
    before: dict
    after: dict


class WebhookUpdate(BaseModel):
    webhook_id: str
    event: str
    task_id: str
    history_items: List[HistoryItem]


@app.post("/handle-task-status-update")
async def handleTaskStatusUpdate(update: WebhookUpdate):
    print(update, update.dict())
    return {"message": "thanks!"}
