# src/gui/file_order_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QHBoxLayout
from src.file_order_manager import FileOrderManager

class FileOrderTab(QWidget):
    """Tab for reordering files via drag-drop.

    Integrates with MainTab for input folder changes.
    """
    def __init__(self, config_manager, parent_window):
        super().__init__()
        self.config_manager = config_manager
        self.parent = parent_window
        self.input_folder = self.parent.main_tab.get_input_folder()  # From MainTab
        self.manager = FileOrderManager(self.input_folder)
        self.layout = QVBoxLayout(self)  # Store layout for reference
        self.init_ui()
        # Connect to input folder changes
        self.parent.main_tab.input_edit.textChanged.connect(self.refresh_list)

    def init_ui(self):
        self.layout.addWidget(QLabel("Drag and drop to reorder files for PDF assembly. Confirm to apply renames."))

        self.file_list = self.manager.get_file_list_widget()
        self.layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_list)
        btn_layout.addWidget(refresh_btn)

        undo_btn = QPushButton("Undo Last Reorder")
        undo_btn.clicked.connect(self.manager.undo_reorder)
        btn_layout.addWidget(undo_btn)

        self.layout.addLayout(btn_layout)

    def refresh_list(self):
        """Reload files if input folder changes by clearing and repopulating the widget."""
        new_folder = self.parent.main_tab.get_input_folder()
        if new_folder != str(self.manager.input_folder) or not os.path.isdir(new_folder):
            if not os.path.isdir(new_folder):
                QMessageBox.warning(self, "Invalid Folder", "Input folder is invalid. Using previous.")
                return
            self.manager = FileOrderManager(new_folder)
        # Clear and repopulate existing widget
        self.manager.files = self.manager.scan_files()
        self.manager.refresh_widget()