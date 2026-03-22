from vql.screens.confirm_modal import ConfirmModal


def test_confirm_modal_exists():
    modal = ConfirmModal(message="Delete 3 rows?")
    assert modal.message == "Delete 3 rows?"


def test_confirm_modal_has_cancel_binding():
    bindings = {b.key for b in ConfirmModal.BINDINGS}
    assert "escape" in bindings
