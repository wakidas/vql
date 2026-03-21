from tui_client.widgets.property_panel import PropertyPanel


def test_property_panel_exists():
    panel = PropertyPanel()
    assert hasattr(panel, "update_properties")


def test_property_panel_update_properties():
    panel = PropertyPanel()
    columns = ["id", "name", "email"]
    row = (1, "alice", "alice@example.com")
    panel.update_properties(columns, row)
    assert panel.properties == [
        ("id", "1"),
        ("name", "alice"),
        ("email", "alice@example.com"),
    ]


def test_property_panel_clear():
    panel = PropertyPanel()
    panel.update_properties(["id"], (1,))
    panel.clear_properties()
    assert panel.properties == []


def test_property_panel_none_value():
    panel = PropertyPanel()
    panel.update_properties(["id", "name"], (1, None))
    assert panel.properties == [("id", "1"), ("name", "NULL")]
