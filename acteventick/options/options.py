from pydantic import BaseModel, Field

from acteventick.options.clock import ClockOptions
from acteventick.options.debug import DebugOptions


class Options(BaseModel):
    clock: ClockOptions = Field(default_factory=ClockOptions)
    debug: DebugOptions = Field(default_factory=DebugOptions)
