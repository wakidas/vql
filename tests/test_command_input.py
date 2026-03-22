from tui_client.screens.main import MainScreen


def test_main_screen_has_colon_binding():
    """colon binding should trigger command_input action."""
    bindings = {b.key: b for b in MainScreen.BINDINGS}
    assert "colon" in bindings
    assert bindings["colon"].action == "command_input"


def test_command_input_initially_hidden_in_css():
    """command-input should have display: none in DEFAULT_CSS."""
    assert "display: none" in MainScreen.DEFAULT_CSS
    assert "#command-input" in MainScreen.DEFAULT_CSS
