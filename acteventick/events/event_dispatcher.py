from collections.abc import Callable
from queue import Queue
from typing import Type

from acteventick.events.event import Event


class EventDispatcher:

    def __init__(self):
        self._queue: Queue[Event] = Queue()
        self._listeners: dict[Type[Event], list[Callable]] = {}

    def push(self, event: Event):
        """Push event to queue"""

        self._queue.put(event)

    def emit(self):
        """Emit all events in queue"""

        while not self._queue.empty():
            event = self._queue.get()
            if type(event) in self._listeners:
                for listener in self._listeners[type(event)]:
                    listener(event)

    def register(self, event: Type[Event], handler: Callable) -> None:
        if self._listeners.get(event) is None:
            self._listeners[event] = []
        self._listeners[event].append(handler)

    def unregister(self, event: Type[Event], handler: Callable) -> None:
        if self._listeners.get(event) is not None:
            return
        self._listeners[event].remove(handler)
