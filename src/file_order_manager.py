# src/file_order_manager.py
# ... existing imports ...

class FileOrderManager:
    # ... existing code ...

    def handle_reorder(self, parent, start, end, destination, row):
        """Stage reorder visually; renaming happens on apply."""
        # No immediate rename; just log for now (apply will handle)
        self.staged_order = [Path(self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole)) for i in range(self.file_list_widget.count())]

    def apply_order(self):
        """Apply staged order by renaming with dynamic prefixes."""
        if not hasattr(self, 'staged_order'):
            return
        if QMessageBox.question(None, "Apply Order", "Apply new order by renaming files?") != QMessageBox.StandardButton.Yes:
            return
        self.previous_order = [str(f) for f in self.files]
        num_files = len(self.staged_order)
        prefix_digits = len(str(num_files))  # Dynamic: 1 for <10, 2 for <100, etc.
        existing_names = set(f.name for f in self.input_folder.iterdir() if f.is_file())
        for idx, old_path in enumerate(self.staged_order):
            try:
                base_name = re.sub(r'^\d+-', '', old_path.stem)
                new_name = f"{idx:0{prefix_digits}d}-{base_name}{old_path.suffix}"
                suffix = 0
                while new_name in existing_names:
                    suffix += 1
                    new_name = f"{idx:0{prefix_digits}d}-{base_name}_{suffix}{old_path.suffix}"
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
        del self.staged_order