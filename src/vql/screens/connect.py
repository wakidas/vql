from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button, Static

from vql.db.config import ConnectionConfig, load_connections, save_connection


class ConnectionList(ModalScreen[ConnectionConfig | None]):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("escape", "cancel", "Cancel"),
        Binding("n", "new_connection", "New"),
    ]

    DEFAULT_CSS = """
    ConnectionList {
        align: center middle;
    }
    ConnectionList > Vertical {
        width: 60;
        max-height: 20;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    ConnectionList .conn-item {
        padding: 0 1;
        height: 1;
    }
    ConnectionList .conn-item.--highlight {
        background: $accent;
        color: $text;
    }
    ConnectionList #title {
        text-style: bold;
        padding-bottom: 1;
        text-align: center;
    }
    ConnectionList #empty {
        color: $text-muted;
        text-align: center;
        padding: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._connections = load_connections()
        self._cursor = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Connections", id="title")
            if not self._connections:
                yield Static("No connections. Press [n] to add.", id="empty")
            else:
                for i, conn in enumerate(self._connections):
                    cls = "conn-item --highlight" if i == 0 else "conn-item"
                    yield Static(
                        f"{conn.name} ({conn.user}@{conn.host}:{conn.port}/{conn.database})",
                        classes=cls,
                        id=f"conn-{i}",
                    )

    def _update_highlight(self) -> None:
        for i in range(len(self._connections)):
            widget = self.query_one(f"#conn-{i}", Static)
            if i == self._cursor:
                widget.set_classes("conn-item --highlight")
            else:
                widget.set_classes("conn-item")

    def action_cursor_down(self) -> None:
        if self._connections and self._cursor < len(self._connections) - 1:
            self._cursor += 1
            self._update_highlight()

    def action_cursor_up(self) -> None:
        if self._connections and self._cursor > 0:
            self._cursor -= 1
            self._update_highlight()

    def on_key(self, event) -> None:
        if event.key == "enter" and self._connections:
            self.dismiss(self._connections[self._cursor])

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_new_connection(self) -> None:
        self.app.push_screen(NewConnectionForm(), self._on_new_connection)

    def _on_new_connection(self, config: ConnectionConfig | None) -> None:
        if config is not None:
            save_connection(config)
            self._connections = load_connections()
            self.dismiss(config)


class NewConnectionForm(ModalScreen[ConnectionConfig | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    NewConnectionForm {
        align: center middle;
    }
    NewConnectionForm > Vertical {
        width: 60;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    NewConnectionForm Label {
        margin-top: 1;
    }
    NewConnectionForm #buttons {
        margin-top: 1;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("New Connection", id="title")
            yield Label("Name")
            yield Input(placeholder="my-local-db", id="name")
            yield Label("Host")
            yield Input(value="localhost", id="host")
            yield Label("Port")
            yield Input(value="5432", id="port")
            yield Label("Database")
            yield Input(placeholder="mydb", id="database")
            yield Label("User")
            yield Input(value="postgres", id="user")
            yield Label("Password")
            yield Input(password=True, id="password")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            try:
                port = int(self.query_one("#port", Input).value)
            except ValueError:
                self.notify("Port must be a number", severity="error")
                return
            config = ConnectionConfig(
                name=self.query_one("#name", Input).value,
                driver="postgres",
                host=self.query_one("#host", Input).value,
                port=port,
                database=self.query_one("#database", Input).value,
                user=self.query_one("#user", Input).value,
                password=self.query_one("#password", Input).value or None,
            )
            self.dismiss(config)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
