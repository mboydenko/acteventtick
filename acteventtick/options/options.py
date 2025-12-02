from pydantic import BaseModel, Field

from acteventtick.options.tps import TPSOptions
from acteventtick.options.debug import DebugOptions


class Options(BaseModel):
    tps: TPSOptions = Field(default_factory=TPSOptions)
    debug: DebugOptions = Field(default_factory=DebugOptions)
