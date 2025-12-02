import time
import pytest
from pytest_mock import MockerFixture

from acteventtick import Action
from acteventtick.events.event import Event
from acteventtick.options.debug import TickDuration
from acteventtick.tick_event import TickEvent
from acteventtick.actions.action_handler import ActionHandler
from acteventtick.options import Options
from acteventtick.loop import ActEventTickLoop


# ----------------------------
# Helpers
# ----------------------------
class MockAction(Action):
    pass


class MockActionHandler(ActionHandler):

    def execute(self, action: MockAction):
        ...


class DummyEvent(Event):
    pass


# ----------------------------
# Tests
# ----------------------------
class TestLoop:
    def test_tick_calls_dispatch_and_emit(self, mocker: MockerFixture):
        """_tick() must call dispatcher.dispatch(), push TickEvent and emit events."""

        options = Options()
        loop = ActEventTickLoop(options)

        dispatcher_mock = mocker.patch.object(loop, "_action_dispatcher")
        emitter_mock = mocker.patch.object(loop, "_event_emitter")

        loop._tick()

        dispatcher_mock.dispatch.assert_called_once()
        emitter_mock.push.assert_called_once()
        pushed_event = emitter_mock.push.call_args[0][0]
        assert isinstance(pushed_event, TickEvent)

        emitter_mock.emit.assert_called_once()


    def test_run_stops_after_one_tick(self, mocker: MockerFixture):
        """run() should execute loop until stop() is called."""

        options = Options()
        options.tps.limit = False  # no sleep between ticks

        loop = ActEventTickLoop(options)

        tick_mock = mocker.patch.object(loop, "_tick")

        # first tick calls stop() automatically
        def stop_after_first_tick(*args, **kwargs):
            loop.stop()

        tick_mock.side_effect = stop_after_first_tick

        loop.run()

        tick_mock.assert_called_once()


    def test_tps_limit_causes_sleep(self, mocker: MockerFixture):
        """When TPS is limited, loop should sleep for (ideal_duration - tick_duration)."""

        options = Options()
        options.tps.limit = 20  # means 1/20 seconds per tick

        loop = ActEventTickLoop(options)

        mocker.patch("time.time", side_effect=[0, 0.01])  # tick took 0.01s
        sleep_mock = mocker.patch("time.sleep")
        tick_mock = mocker.patch.object(loop, "_tick", side_effect=lambda: loop.stop())

        loop.run()

        ideal = 1 / 20  # 0.05
        delay = ideal - 0.01  # 0.04

        sleep_mock.assert_called_once_with(delay)


    def test_tps_negative_delay_causes_no_sleep(self, mocker: MockerFixture):
        """If tick duration exceeds ideal tick time, time.sleep must NOT be called."""

        options = Options()
        options.tps.limit = 10  # 0.1 sec per tick

        loop = ActEventTickLoop(options)

        mocker.patch("time.time", side_effect=[0, 0.2])  # tick lasted 0.2s => too slow
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch.object(loop, "_tick", side_effect=lambda: loop.stop())

        loop.run()

        sleep_mock.assert_not_called()


    def test_debug_tick_duration_logs_when_slow(self, mocker: MockerFixture):
        """If debug.tick_duration.enabled and tick took long enough, logger.debug must be called."""

        options = Options()
        options.debug.tick_duration = TickDuration(min_microseconds=10)  # very low threshold

        loop = ActEventTickLoop(options)

        mocker.patch("time.time", side_effect=[0, 0.00002])  # 20 microseconds

        dispatcher_mock = mocker.patch.object(loop, "_action_dispatcher")
        emitter_mock = mocker.patch.object(loop, "_event_emitter")
        log_mock = mocker.patch("loguru.logger.debug")

        loop._tick()

        log_mock.assert_called_once()


    def test_debug_tick_duration_no_log_if_fast(self, mocker: MockerFixture):
        """If tick is too fast, logger.debug must NOT be called."""

        options = Options()
        options.debug.tick_duration = TickDuration(min_microseconds=1000)  # 1ms threshold

        loop = ActEventTickLoop(options)

        mocker.patch("time.time", side_effect=[0, 0.0001])  # 100 microseconds

        mocker.patch.object(loop, "_action_dispatcher")
        mocker.patch.object(loop, "_event_emitter")
        log_mock = mocker.patch("loguru.logger.debug")

        loop._tick()

        log_mock.assert_not_called()


    def test_register_unregister_action_handler(self, mocker: MockerFixture):
        """register_action_handler and unregister_action_handler must call ActionDispatcher with correct arguments."""

        loop = ActEventTickLoop()
        dispatcher_mock = mocker.patch.object(loop, "_action_dispatcher")

        handler = MockActionHandler()

        loop.register_action_handler(MockAction, handler)
        dispatcher_mock.register.assert_called_once_with(MockAction, handler)

        loop.unregister_action_handler(MockAction, handler)
        dispatcher_mock.unregister.assert_called_once_with(MockAction, handler)


    def test_register_unregister_event_handler(self, mocker: MockerFixture):
        """register_event_handler and unregister_event_handler must call EventEmitter."""

        loop = ActEventTickLoop()
        emitter_mock = mocker.patch.object(loop, "_event_emitter")

        handler = lambda e: None

        loop.register_event_handler(DummyEvent, handler)
        emitter_mock.register.assert_called_once_with(DummyEvent, handler)

        loop.unregister_event_handler(DummyEvent, handler)
        emitter_mock.unregister.assert_called_once_with(DummyEvent, handler)


    def test_push_action_calls_dispatcher(self, mocker: MockerFixture):
        loop = ActEventTickLoop()
        dispatcher_mock = mocker.patch.object(loop, "_action_dispatcher")

        action = MockAction()

        loop.push_action(action)
        dispatcher_mock.push.assert_called_once_with(action)


    def test_push_event_calls_emitter(self, mocker: MockerFixture):
        loop = ActEventTickLoop()
        emitter_mock = mocker.patch.object(loop, "_event_emitter")

        event = DummyEvent()

        loop.push_event(event)
        emitter_mock.push.assert_called_once_with(event)
