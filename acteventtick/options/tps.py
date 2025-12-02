from pydantic import BaseModel, Field


class TPSOptions(BaseModel):
    """Tick per second option"""
    limit: int | None = Field(default=None)
