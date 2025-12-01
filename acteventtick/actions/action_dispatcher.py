import traceback
from queue import Queue
from typing import Type
import time

from loguru import logger

from acteventtick.actions.action import Action
from acteventtick.actions.action_handler import ActionHandler
from acteventtick.options.debug import DebugOptions

def _deb_action_exec_duration(func):

    def action_duration(self: "ActionDispatcher", action: Action, handler: ActionHandler) -> None:

        if not self._debug_options or not self._debug_options.action_exec_duration:
            return func(self, action, handler)

        if type(action) in self._debug_options.action_exec_duration.ignore:
            return func(self, action, handler)

        start_time = time.time()
        result = func(self, action, handler)
        end_time = time.time()
        duration_microseconds = (end_time - start_time) * 1000000
        if duration_microseconds > self._debug_options.action_exec_duration.min_microseconds:
            logger.debug('Duration of {} execution is: {} microseconds'.format(action.__class__.__name__,
                                                                               duration_microseconds))
        return result
    return action_duration


class ActionDispatcher:

    def __init__(self, debug_options: DebugOptions | None = None) -> None:
        self._debug_options = debug_options
        self._queue: Queue[Action] = Queue()
        self._handlers: dict[Type[Action], list[ActionHandler]] = {}

    def register(self, action_type: Type[Action], handler: ActionHandler):
        if self._handlers.get(action_type) is None:
            self._handlers[action_type] = []
        self._handlers[action_type].append(handler)

    def unregister(self, action: Type[Action], handler: ActionHandler):
        if self._handlers.get(action) is None:
            return
        self._handlers[action].remove(handler)
        if len(self._handlers[action]) == 0:
            del self._handlers[action]

    def push(self, action: Action) -> None:
        self._queue.put(action)

    def dispatch(self) -> None:
        while not self._queue.empty():
            action = self._queue.get()
            handlers = self._handlers.get(type(action), [])
            for handler in handlers:
                self._exec_handler(action, handler)

    @_deb_action_exec_duration
    def _exec_handler(self, action: Action, handler: ActionHandler) -> None:
        try:
            handler.execute(action)
        except Exception:
            logger.error('Failed to execute action: {} ({})\n{}'.format(
                action.__class__.__name__, action, str(traceback.format_exc())))