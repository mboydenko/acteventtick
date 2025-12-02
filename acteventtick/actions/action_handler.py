from abc import ABC, abstractmethod

from acteventtick.actions.action import Action

def _check_action_type(method):
    def wrapper(self, action, *args, **kwargs):
        self._check_action_type(action)       # вызываем check() перед execute()
        return method(self, *args, **kwargs)
    return wrapper


class ActionHandler(ABC):

    @abstractmethod
    def execute(self, action: Action) -> None:
        ...
