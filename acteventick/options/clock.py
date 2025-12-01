from pydantic import BaseModel, Field


class ClockOptions(BaseModel):
    min_ticks_in_second: int = Field(default=1)
    max_ticks_in_second: int = Field(default=1000)
