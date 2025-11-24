# Filename: src/gui/cover_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QTextEdit, QPushButton, QColorDialog,
    QSlider, QLabel, QGroupBox, QHBoxLayout, QRadioButton, QComboBox,
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.config import ConfigManager

class CoverTab(QWidget):
    """Cover Editor tab with live preview canvas and Update CSS button."""
    
    def __init__(self, config_manager: ConfigManager, parent_window):
        super().__init__()
        self.config_manager = config_manager
        self.parent = parent_window
        self.cover = config_manager.config['cover']
        
        self.init_ui()
        self.update_preview()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Text Editor
        editor_group = QGroupBox("Cover Text Lines")
        editor_layout = QVBoxLayout(editor_group)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("\n".join(line['text'] for line in self.cover['lines']))
        self.text_edit.textChanged.connect(self.on_text_changed)
        editor_layout.addWidget(self.text_edit)
        layout.addWidget(editor_group)
        
        # Styling Controls
        style_group = QGroupBox("Line Styling (applies to selected line or all)")
        style_layout = QFormLayout(style_group)
        
        # Alignment
        align_layout = QHBoxLayout()
        self.align_radios = {}
        for align in ['left', 'center', 'right']:
            radio = QRadioButton(align.capitalize())
            if align == 'center':
                radio.setChecked(True)
            align_layout.addWidget(radio)
            self.align_radios[align] = radio
        style_layout.addRow("Alignment:", align_layout)
        
        # Font & Size
        font_layout = QHBoxLayout()
        self.font_combo = QComboBox()
        self.font_combo.addItems(['Times New Roman', 'Arial', 'Helvetica', 'Courier'])
        font_layout.addWidget(self.font_combo)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(8, 100)
        self.size_slider.setValue(36)
        font_layout.addWidget(QLabel("Size:"))
        font_layout.addWidget(self.size_slider)
        style_layout.addRow("Font & Size:", font_layout)
        
        # Bold / Italic
        bold_italic_layout = QHBoxLayout()
        self.bold_check = QCheckBox("  Bold")
        self.italic_check = QCheckBox("  Italic")
        bold_italic_layout.addWidget(self.bold_check)
        bold_italic_layout.addWidget(self.italic_check)
        style_layout.addRow("Style:", bold_italic_layout)
        
        apply_btn = QPushButton("Apply Styling")
        apply_btn.clicked.connect(self.apply_styling)
        style_layout.addRow(apply_btn)
        
        layout.addWidget(style_group)
        
        # Global Controls
        global_group = QGroupBox("Global Cover Settings")
        global_layout = QFormLayout(global_group)
        
        bg_btn = QPushButton("Background Color")
        bg_btn.clicked.connect(self.choose_bg_color)
        global_layout.addRow(bg_btn)
        
        padding_label = QLabel("Top Padding (pt):")
        self.padding_slider = QSlider(Qt.Orientation.Horizontal)
        self.padding_slider.setRange(0, 500)
        self.padding_slider.setValue(self.cover['padding_top'])
        self.padding_slider.valueChanged.connect(self.on_padding_changed)
        global_layout.addRow(padding_label, self.padding_slider)
        
        update_css_btn = QPushButton("Update CSS & Refresh Preview")
        update_css_btn.clicked.connect(self.parent.live_preview_tab.refresh_preview)
        global_layout.addRow(update_css_btn)
        
        save_btn = QPushButton("Save as Default")
        save_btn.clicked.connect(self.save_cover_config)
        global_layout.addRow(save_btn)
        
        layout.addWidget(global_group)
        
        # Preview Canvas (simple colored label simulation)
        self.preview_label = QLabel("Cover Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"background: {self.cover['bg_color']}; color: white; font-size: 24pt;")
        self.preview_label.setMinimumHeight(300)
        layout.addWidget(self.preview_label)

    def on_text_changed(self):
        lines = self.text_edit.toPlainText().split('\n')
        self.cover['lines'] = [
            {'text': line.strip(), 'align': 'center', 'font': 'Times New Roman', 'size': 36, 'bold': False, 'italic': False}
            for line in lines if line.strip()
        ]
        self.update_preview()

    def apply_styling(self):
        selected_align = next(k for k, v in self.align_radios.items() if v.isChecked())
        font = self.font_combo.currentText()
        size = self.size_slider.value()
        bold = self.bold_check.isChecked()
        italic = self.italic_check.isChecked()
        
        # Apply to all for simplicity (could detect selection)
        for line in self.cover['lines']:
            line.update({'align': selected_align, 'font': font, 'size': size, 'bold': bold, 'italic': italic})
        self.update_preview()

    def choose_bg_color(self):
        color = QColorDialog.getColor(initial=QColor(self.cover['bg_color']))
        if color.isValid():
            self.cover['bg_color'] = color.name()
            self.update_preview()

    def on_padding_changed(self, value: int):
        self.cover['padding_top'] = value
        self.update_preview()

    def update_preview(self):
        sample_text = "<br>".join(line['text'] for line in self.cover['lines'][:3])
        self.preview_label.setText(f"<h1>{sample_text}</h1>")
        self.preview_label.setStyleSheet(f"background: {self.cover['bg_color']}; color: white;")

    def save_cover_config(self):
        self.config_manager.save_config()
        QMessageBox.information(self, "Saved", "Cover settings saved to config.yaml")