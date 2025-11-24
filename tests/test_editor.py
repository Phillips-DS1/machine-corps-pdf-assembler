# tests/test_editor.py
import pytest
from src.editor import MarkdownEditor

def test_auto_save(tmp_path):
    file = tmp_path / 'test.md'
    file.write_text('initial')
    editor = MarkdownEditor(str(file), lambda: None)
    editor.setPlainText('updated')
    assert file.read_text() == 'updated'

def test_insert_table(editor_fixture):
    editor = editor_fixture
    editor.insert_table()
    assert '| Header1 |' in editor.toPlainText()

def test_insert_image(editor_fixture, monkeypatch):
    editor = editor_fixture
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *args: ('test.png', ''))
    editor.insert_image()
    assert '![Alt Text](test.png)' in editor.toPlainText()  # Updated assertion