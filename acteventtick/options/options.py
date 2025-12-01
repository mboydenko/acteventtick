from pydantic import BaseModel, Field

from acteventtick.options.tps import TPSOption
from acteventtick.options.debug import DebugOptions


class Options(BaseModel):
    tps: TPSOption = Field(default_factory=TPSOption)
    debug: DebugOptions = Field(default_factory=DebugOptions)
