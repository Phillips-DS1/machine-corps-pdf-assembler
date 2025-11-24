# tests/test_themes.py
import pytest
from src.themes import ThemeManager

def test_load_theme():
    tm = ThemeManager()
    css = tm.load_theme('light')
    assert '--primary-color: black;' in css

def test_switch_theme(qapp):
    tm = ThemeManager()
    tm.switch_theme('dark', qapp)
    assert tm.current_theme == 'dark'