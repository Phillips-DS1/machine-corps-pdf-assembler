# tests/test_file_order_manager.py
import pytest
import os
from pathlib import Path
from src.file_order_manager import FileOrderManager

def test_scan_files(tmp_path):
    (tmp_path / '01-test.md').touch()
    fm = FileOrderManager(str(tmp_path))
    assert len(fm.files) == 1
    assert fm.files[0].name == '01-test.md'

def test_handle_reorder(tmp_path, monkeypatch):
    fm = FileOrderManager(str(tmp_path))
    file1 = tmp_path / 'file1.md'
    file2 = tmp_path / 'file2.md'
    file1.touch()
    file2.touch()
    fm.files = [file1, file2]
    fm.get_file_list_widget()
    # Simulate reorder (swap)
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Yes)
    fm.handle_reorder(None, 0, 0, None, 1)
    new_files = fm.scan_files()
    assert new_files[0].name == '00-file2.md'  # After swap
    assert new_files[1].name == '01-file1.md'

def test_undo_reorder(tmp_path):
    fm = FileOrderManager(str(tmp_path))
    file1 = tmp_path / '00-file.md'
    file1.touch()
    fm.files = [file1]
    fm.previous_order = [str(tmp_path / 'original.md')]
    fm.undo_reorder()
    assert (tmp_path / 'original.md').exists()
    assert not file1.exists()

def test_empty_folder(tmp_path):
    fm = FileOrderManager(str(tmp_path))
    assert fm.files == []

def test_conflict_rename(tmp_path):
    fm = FileOrderManager(str(tmp_path))
    file1 = tmp_path / '00-file.md'
    file2 = tmp_path / 'file.md'
    file1.touch()
    file2.touch()
    fm.files = [file2, file1]
    fm.get_file_list_widget()
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.StandardButton.Yes)
    fm.handle_reorder(None, 0, 0, None, 1)  # Attempt reorder causing conflict
    new_files = [f.name for f in fm.scan_files()]
    assert '00-file_1.md' in new_files or similar  # Check for suffix
