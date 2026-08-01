from pydantic import BaseModel, Field
from typing import Any


class CopilotRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class CopilotResponse(BaseModel):
    agent: str
    message: str
    data: dict[str, Any] | list[dict[str, Any]] | None = None
