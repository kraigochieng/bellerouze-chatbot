from datetime import datetime
from typing import Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class IncomingMessage(BaseModel):
    phone_number_id: str
    timestamp: str
    type: Literal["message"]
    from_number: str
    incoming_message: str


class ReplyMessage(BaseModel):
    to_number: str
    message_id: str
    message: str


class StatusUpdate(BaseModel):
    phone_number_id: str
    timestamp: str
    type: Literal["status"]
    status: str
    message_id: str
    recipient_id: str


class MessageWithStatusResponse(BaseModel):
    incoming_message: IncomingMessage
    reply_message: ReplyMessage
    statuses: List[StatusUpdate]


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
