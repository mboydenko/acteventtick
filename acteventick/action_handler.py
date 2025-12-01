from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type

from acteventick.action import Action


T = TypeVar("T", bound=Action)


def _check_action_type(method):
    def wrapper(self, action, *args, **kwargs):
        self._check_action_type(action)       # вызываем check() перед execute()
        return method(self, *args, **kwargs)
    return wrapper


class ActionHandler(Generic[T], ABC):

    def __init__(self, action_type: Type[T]):
        self._action_type = action_type

    @abstractmethod
    def execute(self, action: T) -> None:
        ...
