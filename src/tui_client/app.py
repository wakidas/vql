from __future__ import annotations

from textual.app import App

from tui_client.db.config import ConnectionConfig
from tui_client.db.postgres import PostgresAdapter
from tui_client.screens.main import MainScreen


class TuiClientApp(App):
    TITLE = "tui-client"
    CSS = """
    Screen {
        background: $surface;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.adapter: PostgresAdapter | None = None

    def on_mount(self) -> None:
        main = MainScreen()
        self.push_screen(main)
        from tui_client.screens.connect import ConnectionList
        self.push_screen(ConnectionList(), self._on_initial_connect)

    def _on_initial_connect(self, config: ConnectionConfig | None) -> None:
        if config is None:
            self.exit()
        else:
            self.connect_to_db(config)

    def connect_to_db(self, config: ConnectionConfig) -> None:
        self.run_worker(self._async_connect(config))

    async def _async_connect(self, config: ConnectionConfig) -> None:
        if self.adapter:
            await self.adapter.close()
        self.adapter = PostgresAdapter()
        try:
            await self.adapter.connect(
                host=config.host,
                port=config.port,
                dbname=config.database,
                user=config.user,
                password=config.password,
            )
        except Exception as e:
            self.adapter = None
            self.notify(f"Connection failed: {e}", severity="error")
            return
        main = self.query_one(MainScreen)
        main.adapter = self.adapter
        self.title = f"tui-client - {config.name}"
        await main._load_schema()

    async def on_unmount(self) -> None:
        if self.adapter:
            await self.adapter.close()


def main() -> None:
    app = TuiClientApp()
    app.run()
