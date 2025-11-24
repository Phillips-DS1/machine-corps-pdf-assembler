# Filename: src/gui/main_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog,
    QLabel, QGroupBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from src.config import ConfigManager

class MainTab(QWidget):
    """Main Controls tab for input/output paths, classification, and actions."""
    
    def __init__(self, config_manager: ConfigManager, parent_window):
        super().__init__()
        self.config_manager = config_manager
        self.parent = parent_window
        self.config = config_manager.config
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Input / Output Group
        io_group = QGroupBox("Input & Output")
        io_layout = QFormLayout(io_group)
        
        # Input Folder
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit(self.config['input_folder'])
        self.input_edit.textChanged.connect(lambda t: self.config_manager.set('input_folder', t))
        input_btn = QPushButton("Browse...")
        input_btn.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        io_layout.addRow("Input Markdown Folder:", input_layout)
        
        # Output File
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit(self.config['output_file'])
        self.output_edit.textChanged.connect(lambda t: self.config_manager.set('output_file', t))
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        io_layout.addRow("Output PDF File:", output_layout)
        
        # Classification
        class_layout = QHBoxLayout()
        self.class_edit = QLineEdit(self.config.get('classification', ''))
        self.class_edit.textChanged.connect(lambda t: self.config_manager.set('classification', t))
        class_layout.addWidget(self.class_edit)
        io_layout.addRow("Classification Marking (e.g., CUI // FOUO):", class_layout)
        
        layout.addWidget(io_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.config_manager.save_config)
        actions_layout.addWidget(save_btn)
        
        refresh_btn = QPushButton("Refresh Live Preview")
        refresh_btn.clicked.connect(self.parent.live_preview_tab.refresh_preview)
        actions_layout.addWidget(refresh_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()

    def browse_input(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Input Folder", self.input_edit.text()
        )
        if folder:
            self.input_edit.setText(folder)

    def browse_output(self):
        file, _ = QFileDialog.getSaveFileName(
            self, "Select Output PDF", self.output_edit.text(), "PDF Files (*.pdf)"
        )
        if file:
            self.output_edit.setText(file)

    def get_input_folder(self) -> str:
        return self.input_edit.text().strip()

    def get_output_file(self) -> str:
        return self.output_edit.text().strip()