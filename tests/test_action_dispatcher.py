from unittest.mock import call

from pytest_mock import MockerFixture

from acteventtick import Action, ActionHandler
from acteventtick.actions import ActionDispatcher


class MockAction(Action):
    payload: int


class MockActionHandler(ActionHandler[MockAction]):
    def __init__(self):
        super().__init__(MockAction)

    def execute(self, action: Action):
        ...


def assert_exec_calls(handler, expected_actions):
    """Check call count and call sequence."""
    assert handler.execute.call_count == len(expected_actions)
    handler.execute.assert_has_calls([call(a) for a in expected_actions])


def test_dispatcher(mocker: MockerFixture):
    dispatcher = ActionDispatcher()

    handlers = [MockActionHandler() for _ in range(3)]
    actions = [MockAction(payload=i) for i in (1, 2, 3)]

    # Mock the execute() method for all handlers
    for h in handlers:
        h.execute = mocker.Mock()

    # Register all handlers
    for h in handlers:
        dispatcher.register(MockAction, h)

    # First dispatch cycle
    for a in actions:
        dispatcher.push(a)

    # No calls should happen before dispatch()
    for h in handlers:
        assert h.execute.call_count == 0

    dispatcher.dispatch()

    # After dispatch, each handler should receive 3 calls
    for h in handlers:
        assert_exec_calls(h, actions)

    # --- Unregister the first two handlers ---
    for h in handlers[:2]:
        dispatcher.unregister(MockAction, h)

    # Second dispatch cycle
    for a in actions:
        dispatcher.push(a)
    dispatcher.dispatch()

    # First two handlers should not receive new calls
    for h in handlers[:2]:
        assert_exec_calls(h, actions)

    # Third handler should receive 3 additional calls
    assert_exec_calls(handlers[-1], actions + actions)

    # --- Unregister the last remaining handler ---
    dispatcher.unregister(MockAction, handlers[-1])

    # Third dispatch cycle
    for a in actions:
        dispatcher.push(a)
    dispatcher.dispatch()

    # Third handler should not receive additional calls now
    assert_exec_calls(handlers[-1], actions + actions)
