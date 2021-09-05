import datetime
from typing import Optional, List

from pydantic import BaseModel


class CompletedTaskLog(BaseModel):
    timestamp: datetime.datetime
    task_id: str
    task_name: str
    effort: float


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

    def get_datetime(self):
        return datetime.datetime.fromtimestamp(int(self.date) / 1000)


class WebhookUpdate(BaseModel):
    webhook_id: str
    event: str
    task_id: str
    history_items: List[HistoryItem]
