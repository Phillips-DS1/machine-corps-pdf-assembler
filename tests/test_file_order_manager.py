# tests/test_file_order_manager.py
# ... existing tests ...

def test_apply_order(tmp_path, monkeypatch):
    fm = FileOrderManager(str(tmp_path))
    file1 = tmp_path / 'file1.md'
    file2 = tmp_path / 'file2.md'
    file1.touch()
    file2.touch()
    fm.files = [file1, file2]
    fm.get_file_list_widget()
    # Simulate staged swap
    fm.staged_order = [file2, file1]
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Yes)
    fm.apply_order()
    new_files = fm.scan_files()
    assert new_files[0].name == '0-file2.md'  # Dynamic prefix (1 digit for 2 files)
    assert new_files[1].name == '1-file1.md'  # Fixed assertion