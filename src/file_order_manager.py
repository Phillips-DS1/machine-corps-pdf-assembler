# src/file_order_manager.py
import os
import re
import logging
from pathlib import Path
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from src.utils import discover_files  # Integrate with existing utils

logger = logging.getLogger(__name__)

class FileOrderManager:
    """Manages file scanning and reordering with prefix renaming.

    Uses src/utils.discover_files for scanning consistency.
    """
    def __init__(self, input_folder):
        self.input_folder = Path(input_folder)
        self.files = self.scan_files()
        self.file_list_widget = None
        self.previous_order = []  # For basic undo

    def scan_files(self):
        """Scan and sort Markdown files using utils.discover_files."""
        try:
            return discover_files(str(self.input_folder))
        except ValueError as e:
            logger.error(f"Scan failed: {e}")
            return []

    def get_prefix_order(self, filename: str) -> int:
        """Extract numeric prefix for sorting (defaults to 999 if none)."""
        match = re.match(r'(\d+)-', filename)
        return int(match.group(1)) if match else 999  # 999 ensures unprefixed files sort last

    def get_file_list_widget(self):
        """Create draggable list widget."""
        self.file_list_widget = QListWidget()
        self.file_list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        for file in self.files:
            item = QListWidgetItem(file.name)
            item.setData(Qt.ItemDataRole.UserRole, str(file))
            self.file_list_widget.addItem(item)
        self.file_list_widget.model().rowsMoved.connect(self.handle_reorder)
        return self.file_list_widget

    def handle_reorder(self, parent, start, end, destination, row):
        """Rename files with prefixes on reorder, with confirmation and conflict handling.

        Confirmation is post-drag due to Qt's rowsMoved signal timing.
        Conflict resolution: Appends suffix if name exists (e.g., _1).
        """
        if QMessageBox.question(None, "Confirm Reorder", "Reorder complete. Apply changes by renaming files with prefixes?") != QMessageBox.StandardButton.Yes:
            self.refresh_widget()  # Revert visual order if canceled
            return
        self.previous_order = [str(f) for f in self.files]  # Save for undo
        new_order = [Path(self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole)) for i in range(self.file_list_widget.count())]
        existing_names = set(f.name for f in self.input_folder.iterdir() if f.is_file())
        for idx, old_path in enumerate(new_order):
            try:
                base_name = re.sub(r'^\d+-', '', old_path.stem)
                new_name = f"{idx:02d}-{base_name}{old_path.suffix}"
                suffix = 0
                while new_name in existing_names:
                    suffix += 1
                    new_name = f"{idx:02d}-{base_name}_{suffix}{old_path.suffix}"
                new_path = self.input_folder / new_name
                if str(old_path) != str(new_path):
                    logger.info(f"Renaming {old_path} to {new_path}")
                    old_path.rename(new_path)
                existing_names.add(new_name)
            except (PermissionError, FileNotFoundError, OSError) as e:
                logger.error(f"Rename failed: {e}")
                QMessageBox.critical(None, "Rename Error", f"Failed to rename {old_path}: {str(e)}")
        self.files = self.scan_files()
        self.refresh_widget()

    def refresh_widget(self):
        """Refresh the list after changes."""
        self.file_list_widget.clear()
        for file in self.files:
            item = QListWidgetItem(file.name)
            item.setData(Qt.ItemDataRole.UserRole, str(file))
            self.file_list_widget.addItem(item)

    def undo_reorder(self):
        """Basic undo by reverting to previous order (rename back)."""
        if not self.previous_order:
            QMessageBox.information(None, "Undo", "No previous order to undo.")
            return
        for old_path_str, new_path in zip(self.previous_order, self.files):
            try:
                if Path(old_path_str).name != new_path.name:
                    new_path.rename(old_path_str)
            except (PermissionError, FileNotFoundError, OSError) as e:
                logger.error(f"Undo failed: {e}")
                QMessageBox.critical(None, "Undo Error", f"Failed to undo {new_path}: {str(e)}")
        self.files = self.scan_files()
        self.refresh_widget()
        self.previous_order = []
