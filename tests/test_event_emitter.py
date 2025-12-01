from unittest.mock import call

from pytest_mock import MockerFixture

from acteventtick import Event
from acteventtick.events import EventEmitter, event_emitter, event


def assert_exec_calls(handler, expected_events):
    """Check call count and call sequence."""
    assert handler.call_count == len(expected_events)
    handler.assert_has_calls([call(a) for a in expected_events])


class MockEvent(Event):
    payload: int


def test_emitter(mocker: MockerFixture) -> None:
    event_emitter = EventEmitter()

    events = [MockEvent(payload=i) for i in range(3)]
    handlers = [mocker.Mock() for _ in range(3)]

    for handler in handlers:
        event_emitter.register(MockEvent, handler)

    for event in events:
        event_emitter.push(event)

    # No calls should happen before emit()
    for h in handlers:
        assert h.execute.call_count == 0

    event_emitter.emit()

    # After emit, each handler should receive 3 calls
    for h in handlers:
        assert_exec_calls(h, events)


    # --- Unregister the first two handlers ---
    for h in handlers[:2]:
        event_emitter.unregister(MockEvent, h)

    # Second dispatch cycle
    for e in events:
        event_emitter.push(e)
    event_emitter.emit()

    # First two handlers should not receive new calls
    for h in handlers[:2]:
        assert_exec_calls(h, events)

    # Third handler should receive 3 additional calls
    assert_exec_calls(handlers[-1], events + events)

    # --- Unregister the last remaining handler ---
    event_emitter.unregister(MockEvent, handlers[-1])

    # Third emit cycle
    for e in events:
        event_emitter.push(e)
    event_emitter.emit()

    # Third handler should not receive additional calls now
    assert_exec_calls(handlers[-1], events + events)
