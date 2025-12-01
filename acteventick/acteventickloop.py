import time
from typing import Callable, Type
from loguru import logger

from acteventick import Action
from acteventick.event import Event
from acteventick.event_dispatcher import EventDispatcher
from acteventick.action_handler import ActionHandler
from acteventick.options import Options
from acteventick.tick_event import TickEvent
from acteventick.action_dispatcher import ActionDispatcher


def _deb_tick_duration(func):
    def tick_duration(self: "ActEvenTickLoop", *args, **kwargs):
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

class ActEvenTickLoop:

    def __init__(self, options: Options):
        self._action_dispatcher = ActionDispatcher(debug_options=options.debug)
        self._event_emitter = EventDispatcher()
        self._options = options
        self._running = False

    def run(self) -> None:
        self._running = True
        self._loop()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            start = time.time()

            self._tick()

            end = time.time()
            tick_duration = end - start
            ideal_duration = 1.0 / self._options.clock.max_ticks_in_second
            max_allowed_duration = 1.0 / self._options.clock.min_ticks_in_second

            if tick_duration > max_allowed_duration:
                logger.error(
                    f'Tick too long: {tick_duration * 1e6:.0f} us\n'
                    f'Max allowed duration: {max_allowed_duration * 1e6:.0f} us\n'
                    f'Check performance of your actions/events.'
                )
                continue

            delay = ideal_duration - tick_duration

            if delay < 0:
                continue

            time.sleep(delay)

    @_deb_tick_duration
    def _tick(self) -> None:
        self._action_dispatcher.dispatch()
        self._event_emitter.push(TickEvent())
        self._event_emitter.emit()

    def register_event_handler(self, event: Type[Event], handler: Callable) -> None:
        self._event_emitter.register(event, handler)

    def unregister_event_handler(self, event: Type[Event], handler: Callable) -> None:
        self._event_emitter.unregister(event, handler)

    def register_action_handler(self, action: Type[Action], handler: ActionHandler) -> None:
        self._action_dispatcher.register(action, handler)

    def unregister_action_handler(self, action: Type[Action], handler: ActionHandler) -> None:
        self._action_dispatcher.unregister(action, handler)

    def push_event(self, event: Event) -> None:
        self._event_emitter.push(event)

    def push_action(self, action: Action) -> None:
        self._action_dispatcher.push(action)
