import time
from typing import Callable, Type
from loguru import logger

from acteventtick import Action
from acteventtick.events.event import Event
from acteventtick.events.event_emitter import EventEmitter
from acteventtick.actions.action_handler import ActionHandler
from acteventtick.options import Options
from acteventtick.tick_event import TickEvent
from acteventtick.actions.action_dispatcher import ActionDispatcher


def _deb_tick_duration(func):
    def tick_duration(self: "ActEventTickLoop", *args, **kwargs):
        if not self._options.debug.tick_duration:
            return func(self, *args, **kwargs)

        start = time.time()
        result = func(self, *args, **kwargs)
        end = time.time()
        duration = (end - start) * 1000000
        if duration > self._options.debug.tick_duration.min_microseconds:
            logger.debug('Time of tick is {} microseconds'.format(duration))
        return result
    return tick_duration

class ActEventTickLoop:
    """
    Lifecycle
    1. Execute actions
    2. Emit events
    """

    def __init__(self, options: Options | None = None):
        if not options:
            options = Options()

        self._options = options
        self._action_dispatcher = ActionDispatcher(debug_options=options.debug)
        self._event_emitter = EventEmitter()
        self._options = options
        self._running = False

    def run(self) -> None:
        self._running = True
        self._loop()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            if not self._options.tps.limit:
                self._tick()
                continue

            start = time.time()
            self._tick()
            end = time.time()

            tick_duration = end - start
            ideal_duration = 1.0 / self._options.tps.limit
            delay = ideal_duration - tick_duration

            if delay < 0:
                continue

            time.sleep(delay)

    @_deb_tick_duration
    def _tick(self) -> None:
        self._action_dispatcher.dispatch()
        self._event_emitter.push(TickEvent())
        self._event_emitter.emit()

    def register_event_handler(self, event_type: Type[Event], handler: Callable) -> None:
        self._event_emitter.register(event_type, handler)

    def unregister_event_handler(self, event_type: Type[Event], handler: Callable) -> None:
        self._event_emitter.unregister(event_type, handler)

    def register_action_handler(self, action_type: Type[Action], handler: ActionHandler) -> None:
        self._action_dispatcher.register(action_type, handler)

    def unregister_action_handler(self, action_type: Type[Action], handler: ActionHandler) -> None:
        self._action_dispatcher.unregister(action_type, handler)

    def push_event(self, event: Event) -> None:
        self._event_emitter.push(event)

    def push_action(self, action: Action) -> None:
        self._action_dispatcher.push(action)
