# Filename: src/gui/live_preview_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from src.config import ConfigManager
from src.html_generator import HTMLGenerator

class LivePreviewTab(QWidget):
    """Live Preview tab with embedded QWebEngineView for accurate HTML/CSS rendering."""
    
    def __init__(self, config_manager: ConfigManager, html_generator: HTMLGenerator, parent_window):
        super().__init__()
        self.config_manager = config_manager
        self.html_generator = html_generator
        self.parent = parent_window
        self.input_folder = self.parent.main_tab.get_input_folder
        
        self.init_ui()
        self.refresh_preview()  # Initial load

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        top_bar = QVBoxLayout()
        title = QLabel("<h2>Live Preview – What You See Is What You Get</h2>")
        title.setStyleSheet("color: navy;")
        top_bar.addWidget(title)
        
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.setToolTip("Re-generate HTML with current settings and reload")
        refresh_btn.clicked.connect(self.refresh_preview)
        btn_layout.addWidget(refresh_btn)
        
        export_html_btn = QPushButton("Export HTML for Review")
        export_html_btn.setToolTip("Save current HTML to file for external viewing")
        export_html_btn.clicked.connect(self.export_html)
        btn_layout.addWidget(export_html_btn)
        
        top_bar.addLayout(btn_layout)
        layout.addLayout(top_bar)
        
        self.webview = QWebEngineView()
        self.webview.setZoomFactor(1.0)
        layout.addWidget(self.webview, stretch=1)

    def refresh_preview(self):
        try:
            input_folder = self.parent.main_tab.get_input_folder()
            if not input_folder or not os.path.isdir(input_folder):
                self.webview.setHtml("<h3 style='color:red;'>Invalid or empty input folder</h3>")
                return
                
            self.parent.update_status("Generating live preview...")
            html_content = self.html_generator.generate_full_html(input_folder)
            css_content = self.config_manager.update_css_placeholders(
                self.config_manager._load_base_css() if hasattr(self.config_manager, '_load_base_css') else ""
            )
            full_html = f"""
            <html>
                <head>
                    <style>{css_content}</style>
                </head>
                <body>{html_content}</body>
            </html>
            """
            self.webview.setHtml(full_html, QUrl("file://"))
            self.parent.update_status("Live preview updated")
        except Exception as e:
            error_html = f"<h3 style='color:red;'>Preview failed: {str(e)}</h3>"
            self.webview.setHtml(error_html)
            QMessageBox.critical(self, "Preview Error", str(e))

    def export_html(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export HTML Preview", "preview.html", "HTML Files (*.html)"
            )
            if file_path:
                html_content = self.html_generator.generate_full_html(self.parent.main_tab.get_input_folder())
                css_content = self.config_manager.update_css_placeholders(
                    self.config_manager._load_base_css() if hasattr(self.config_manager, '_load_base_css') else ""
                )
                full_html = f"""
                <!DOCTYPE html>
                <html>
                    <head>
                        <meta charset="utf-8">
                        <title>Machine Corps Preview</title>
                        <style>{css_content}</style>
                    </head>
                    <body>{html_content}</body>
                </html>
                """
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                QMessageBox.information(self, "Exported", f"HTML preview saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))