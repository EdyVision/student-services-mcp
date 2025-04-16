from typing import Optional

from .response import BaseResponse
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Model for chat request
    """

    message: str
    recipient_id: Optional[str] = None


class ChatResult(BaseModel):
    context: str
    question: str
    answer: str


class ChatResponse(BaseResponse):
    result: Optional[ChatResult] = None
