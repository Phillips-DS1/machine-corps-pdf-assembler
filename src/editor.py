# src/editor.py
from PyQt6.QtWidgets import QTextEdit, QToolBar, QAction, QComboBox, QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon

class MarkdownEditor(QTextEdit):
    """Editable Markdown viewer with toolbar for formatting, bound to file."""
    def __init__(self, file_path, on_save_callback, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.on_save = on_save_callback
        self.document().contentsChanged.connect(self.auto_save)
        self.load_file()
        self.add_toolbar()

    # ... existing methods ...

    def add_toolbar(self):
        """Add formatting toolbar with actions for bold, italic, fonts, tables, images."""
        toolbar = QToolBar(self.parent())
        bold_act = QAction(QIcon('resources/icons/bold.png'), 'Bold', self)  # Assume icon paths exist
        bold_act.triggered.connect(lambda: self.insert_text('**', '**'))
        toolbar.addAction(bold_act)

        italic_act = QAction(QIcon('resources/icons/italic.png'), 'Italic', self)
        italic_act.triggered.connect(lambda: self.insert_text('*', '*'))
        toolbar.addAction(italic_act)

        font_combo = QComboBox()
        font_combo.addItems(['# H1', '## H2', '### H3'])
        font_combo.currentTextChanged.connect(self.apply_header)
        toolbar.addWidget(font_combo)

        table_act = QAction(QIcon('resources/icons/table.png'), 'Insert Table', self)
        table_act.triggered.connect(self.insert_table)
        toolbar.addAction(table_act)

        image_act = QAction(QIcon('resources/icons/image.png'), 'Insert Image', self)
        image_act.triggered.connect(self.insert_image)
        toolbar.addAction(image_act)
        # Signal to parent to add toolbar, e.g., self.parent().addToolBar(toolbar) if appropriate