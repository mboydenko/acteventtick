from enum import IntEnum

from pydantic import BaseModel, Field


class TPSOption(BaseModel):
    """Tick per second option"""
    limit: int | None = Field(default=None)
