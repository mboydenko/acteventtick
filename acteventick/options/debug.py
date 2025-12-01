from typing import Type

from pydantic import BaseModel, Field

from acteventick.actions.action import Action
from acteventick.events.event import Event


class DebugOptions(BaseModel):
    action_exec_duration: "ActionExecDuration | None" = Field(default=None)
    event_exec_duration: "EventExecDuration | None" = Field(default=None)
    tick_duration: "TickDuration | None" = Field(default=None)


class ActionExecDuration(BaseModel):
    min_microseconds: int  = Field(default=0)
    ignore: list[Type[Action]] = Field(default_factory=list)


class EventExecDuration(BaseModel):
    min_microseconds: int | None = Field(default=None)
    ignore: list[Type[Event]] = Field(default_factory=list)


class TickDuration(BaseModel):
    min_microseconds: int = Field(default=0)
