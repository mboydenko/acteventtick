from collections.abc import Callable
from queue import Queue
from typing import Type, Any

from acteventtick.events.event import Event


class EventEmitter:

    def __init__(self):
        self._queue: Queue[Event] = Queue()
        self._listeners: dict[Type[Event], list[Callable[[Event], Any]]] = {}

    def push(self, event: Event):
        """Push event to queue"""

        self._queue.put(event)

    def emit(self):
        """Emit all events in queue"""

        while not self._queue.empty():
            event = self._queue.get()
            if type(event) in self._listeners:
                listeners = self._listeners.get(type(event), [])
                for listener in listeners:
                    listener(event)

    def register(self, event: Type[Event], handler: Callable[[Event], Any]) -> None:
        if self._listeners.get(event) is None:
            self._listeners[event] = []
        self._listeners[event].append(handler)
        if len(self._listeners[event]) == 0:
            del self._listeners[event]

    def unregister(self, event: Type[Event], handler: Callable) -> None:
        if self._listeners.get(event) is None:
            return
        self._listeners[event].remove(handler)
