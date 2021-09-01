from typing import List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class HistoryItemData(BaseModel):
    status_type: str


class HistoryItem(BaseModel):
    id: str
    type: int
    date: str
    field: str
    parent_id: str
    data: HistoryItemData
    source: str
    user: dict
    before: dict
    after: dict


class WebhookUpdate(BaseModel):
    webhook_id: str
    event: str
    task_id: str
    history_item: List[HistoryItem]


@app.post("/handle-task-status-update")
async def handleTaskStatusUpdate(request: Dict[Any, Any]):
    print(request)
    return {"message": "thanks!"}
