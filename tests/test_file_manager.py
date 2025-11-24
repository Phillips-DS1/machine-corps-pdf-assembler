# tests/test_file_manager.py
import pytest
from src.file_manager import FileManager

def test_scan_files(tmp_path):
    (tmp_path / '001-test.md').touch()
    fm = FileManager(str(tmp_path))
    assert len(fm.files) == 1

def test_reorder_files(tmp_path):
    fm = FileManager(str(tmp_path))
    (tmp_path / 'file1.md').touch()
    (tmp_path / 'file2.md').touch()
    fm.files = [tmp_path / 'file1.md', tmp_path / 'file2.md']
    # Simulate reorder (swap)
    fm.reorder_files(None, 0, 0, None, 1)  # Mock signal params
    new_files = fm.scan_files()
    assert new_files[0].name.startswith('000-')
    assert new_files[1].name.startswith('001-')