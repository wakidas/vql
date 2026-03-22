from tui_client.screens.edit_modal import EditCellModal


def test_edit_cell_modal_exists():
    modal = EditCellModal(column_name="name", current_value="alice")
    assert modal.column_name == "name"
    assert modal.current_value == "alice"


def test_edit_cell_modal_null_value():
    modal = EditCellModal(column_name="name", current_value=None)
    assert modal.current_value is None
