import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    username: str
    auth_token: str
    clickup_email: str
    clickup_api_token: str


class CompletedTaskLog(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime.datetime
    task_id: str
    task_name: str
    points: float = 1.0
    username: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


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
