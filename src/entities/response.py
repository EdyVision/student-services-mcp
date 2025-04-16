from typing import Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = False
    error_message: Optional[str] = None
