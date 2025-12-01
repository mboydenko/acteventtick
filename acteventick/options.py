from pydantic import BaseModel, Field

from acteventick.clock_options import ClockOptions
from acteventick.debug_options import DebugOptions


class Options(BaseModel):
    clock: ClockOptions = Field(default_factory=ClockOptions)
    debug: DebugOptions = Field(default_factory=DebugOptions)
