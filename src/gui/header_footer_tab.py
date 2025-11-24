# Filename: src/gui/header_footer_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QTextEdit, QPushButton, QColorDialog,
    QSlider, QLabel, QGroupBox, QHBoxLayout, QRadioButton, QComboBox,
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.config import ConfigManager

class HeaderFooterTab(QWidget):
    """Header and Footer Editor tab with live preview and Update CSS button."""
    
    def __init__(self, config_manager: ConfigManager, parent_window):
        super().__init__()
        self.config_manager = config_manager
        self.parent = parent_window
        self.header = config_manager.config['header']
        self.footer = config_manager.config['footer']
        
        self.init_ui()
        self.update_preview()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header Editor
        header_group = QGroupBox("Running Header")
        header_layout = QVBoxLayout(header_group)
        self.header_text = QTextEdit()
        self.header_text.setPlainText("\n".join(line['text'] for line in self.header['lines']))
        self.header_text.textChanged.connect(self.on_header_text_changed)
        header_layout.addWidget(self.header_text)
        layout.addWidget(header_group)
        
        # Footer Editor
        footer_group = QGroupBox("Running Footer")
        footer_layout = QVBoxLayout(footer_group)
        self.footer_text = QTextEdit()
        self.footer_text.setPlainText("\n".join(line['text'] for line in self.footer['lines']))
        self.footer_text.textChanged.connect(self.on_footer_text_changed)
        footer_layout.addWidget(self.footer_text)
        layout.addWidget(footer_group)
        
        # Shared Styling Controls
        style_group = QGroupBox("Styling (applies to selected section)")
        style_layout = QFormLayout(style_group)
        
        align_layout = QHBoxLayout()
        self.align_radios = {}
        for align in ['left', 'center', 'right']:
            radio = QRadioButton(align.capitalize())
            if align == 'center':
                radio.setChecked(True)
            align_layout.addWidget(radio)
            self.align_radios[align] = radio
        style_layout.addRow("Alignment:", align_layout)
        
        font_layout = QHBoxLayout()
        self.font_combo = QComboBox()
        self.font_combo.addItems(['Times New Roman', 'Arial', 'Helvetica', 'Courier'])
        font_layout.addWidget(self.font_combo)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(6, 18)
        self.size_slider.setValue(10)
        font_layout.addWidget(QLabel("Size:"))
        font_layout.addWidget(self.size_slider)
        style_layout.addRow("Font & Size:", font_layout)
        
        style_checks = QHBoxLayout()
        self.bold_check = QCheckBox("Bold")
        self.italic_check = QCheckBox("Italic")
        style_checks.addWidget(self.bold_check)
        style_checks.addWidget(self.italic_check)
        style_layout.addRow("Style:", style_checks)
        
        apply_header = QPushButton("Apply to Header")
        apply_header.clicked.connect(self.apply_to_header)
        apply_footer = QPushButton("Apply to Footer")
        apply_footer.clicked.connect(self.apply_to_footer)
        apply_row = QHBoxLayout()
        apply_row.addWidget(apply_header)
        apply_row.addWidget(apply_footer)
        style_layout.addRow(apply_row)
        
        layout.addWidget(style_group)
        
        # Height & Color
        height_group = QGroupBox("Margins & Colors")
        height_layout = QFormLayout(height_group)
        
        self.header_height = QSlider(Qt.Orientation.Horizontal)
        self.header_height.setRange(10, 100)
        self.header_height.setValue(self.header['height'])
        self.header_height.valueChanged.connect(lambda v: self.header.update({'height': v}) or self.parent.live_preview_tab.refresh_preview())
        height_layout.addRow("Header Height (pt):", self.header_height)
        
        header_color_btn = QPushButton("Header Text Color")
        header_color_btn.clicked.connect(self.choose_header_color)
        height_layout.addRow(header_color_btn)
        
        self.footer_height = QSlider(Qt.Orientation.Horizontal)
        self.footer_height.setRange(10, 100)
        self.footer_height.setValue(self.footer['height'])
        self.footer_height.valueChanged.connect(lambda v: self.footer.update({'height': v}) or self.parent.live_preview_tab.refresh_preview())
        height_layout.addRow("Footer Height (pt):", self.footer_height)
        
        footer_color_btn = QPushButton("Footer Text Color")
        footer_color_btn.clicked.connect(self.choose_footer_color)
        height_layout.addRow(footer_color_btn)
        
        update_css_btn = QPushButton("Update CSS & Refresh Preview")
        update_css_btn.clicked.connect(self.parent.live_preview_tab.refresh_preview)
        height_layout.addRow(update_css_btn)
        
        save_btn = QPushButton("Save as Default")
        save_btn.clicked.connect(self.save_config)
        height_layout.addRow(save_btn)
        
        layout.addWidget(height_group)
        
        # Simple Preview
        self.preview_label = QLabel("Header | Body | Footer Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background: white; border: 1px solid gray; min-height: 100px;")
        layout.addWidget(self.preview_label)
        self.update_preview()

    def on_header_text_changed(self):
        lines = self.header_text.toPlainText().split('\n')
        self.header['lines'] = [{'text': line.strip(), 'align': 'center', 'font': 'Times New Roman', 'size': 10, 'bold': False, 'italic': False} for line in lines if line.strip()]

    def on_footer_text_changed(self):
        lines = self.footer_text.toPlainText().split('\n')
        self.footer['lines'] = [{'text': line.strip(), 'align': 'center', 'font': 'Times New Roman', 'size': 10, 'bold': False, 'italic': False} for line in lines if line.strip()]

    def apply_to_header(self):
        self._apply_styling(self.header['lines'])

    def apply_to_footer(self):
        self._apply_styling(self.footer['lines'])

    def _apply_styling(self, lines):
        align = next(k for k, v in self.align_radios.items() if v.isChecked())
        font = self.font_combo.currentText()
        size = self.size_slider.value()
        bold = self.bold_check.isChecked()
        italic = self.italic_check.isChecked()
        for line in lines:
            line.update({'align': align, 'font': font, 'size': size, 'bold': bold, 'italic': italic})
        self.parent.live_preview_tab.refresh_preview()

    def choose_header_color(self):
        color = QColorDialog.getColor(initial=QColor(self.header['color']))
        if color.isValid():
            self.header['color'] = color.name()
            self.parent.live_preview_tab.refresh_preview()

    def choose_footer_color(self):
        color = QColorDialog.getColor(initial=QColor(self.footer['color']))
        if color.isValid():
            self.footer['color'] = color.name()
            self.parent.live_preview_tab.refresh_preview()

    def update_preview(self):
        header_text = "<br>".join(line['text'] for line in self.header['lines'])
        footer_text = "<br>".join(line['text'] for line in self.footer['lines'])
        self.preview_label.setText(f"<small style='color: {self.header['color']}'>{header_text}</small><hr><small style='color: {self.footer['color']}'>{footer_text}</small>")

    def save_config(self):
        self.config_manager.save_config()
        QMessageBox.information(self, "Saved", "Header/Footer settings saved")