# src/file_manager.py
import os
import re
import logging
from pathlib import Path
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file scanning, ordering, and dynamic arrangement for the PDF assembler."""
    def __init__(self, input_folder):
        self.input_folder = Path(input_folder)
        self.files = self.scan_files()
        self.file_list_widget = None  # Store widget reference

    def scan_files(self):
        """Scan for Markdown files in the input folder."""
        return sorted([f for f in self.input_folder.glob('*.md') if f.is_file()], key=lambda f: f.name)

    def get_file_list_widget(self):
        """Create a draggable QListWidget for file reordering."""
        self.file_list_widget = QListWidget()
        self.file_list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        for file in self.files:
            item = QListWidgetItem(file.name)
            item.setData(Qt.ItemDataRole.UserRole, str(file))
            self.file_list_widget.addItem(item)
        self.file_list_widget.model().rowsMoved.connect(self.reorder_files)
        return self.file_list_widget

    def reorder_files(self, parent, start, end, destination, row):
        """Reorder physical files based on list movement (e.g., rename with numeric prefixes), handling conflicts."""
        if not self.file_list_widget:
            logger.error("File list widget not initialized")
            return
        # Extract current order
        new_order = [self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.file_list_widget.count())]
        # Rename with prefixes, avoiding conflicts
        existing_names = set(f.name for f in self.input_folder.glob('*.md'))
        for idx, old_path_str in enumerate(new_order):
            old_path = Path(old_path_str)
            base_name = re.sub(r'^\d{3}-', '', old_path.stem)
            new_name = f"{idx:03d}-{base_name}.md"
            # If conflict, append suffix
            suffix = 0
            while new_name in existing_names:
                suffix += 1
                new_name = f"{idx:03d}-{base_name}_{suffix}.md"
            new_path = self.input_folder / new_name
            if old_path_str != str(new_path):
                logger.info(f"Renaming {old_path} to {new_path}")
                old_path.rename(new_path)
            existing_names.add(new_name)
        self.files = self.scan_files()  # Refresh

    def add_image_placeholder(self, file_path, placeholder):
        """Insert a placeholder like [[image:placeholder]] into the Markdown file."""
        try:
            with open(file_path, 'a') as f:
                f.write(f'\n[[image:{placeholder}]]')
        except IOError as e:
            logger.error(f"Failed to add placeholder: {e}")
            raise ValueError(f"Failed to add placeholder: {e}")