# Filename: src/gui/main_window.py
import sys
import os
import platform
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

from src.config import ConfigManager
from src.html_generator import HTMLGenerator
from src.pdf_renderer import PDFRenderer
from src.gui.build_thread import BuildThread
from src.gui.main_tab import MainTab
from src.gui.cover_tab import CoverTab
from src.gui.header_footer_tab import HeaderFooterTab
from src.gui.live_preview_tab import LivePreviewTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        self.html_generator = HTMLGenerator(self.config_manager)
        self.pdf_renderer = PDFRenderer(self.config_manager)
        
        self.setWindowTitle(self.config['static_strings']['app_title'])
        self.resize(1200, 800)
        self.setMinimumSize(1000, 600)
        
        self.init_ui()
        self.update_status(self.config['static_strings']['status_ready'])

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=1)

        # Add tabs
        self.main_tab = MainTab(self.config_manager, self)
        self.cover_tab = CoverTab(self.config_manager, self)
        self.header_footer_tab = HeaderFooterTab(self.config_manager, self)
        self.live_preview_tab = LivePreviewTab(self.config_manager, self.html_generator, self)

        self.tabs.addTab(self.main_tab, "Main Controls")
        self.tabs.addTab(self.cover_tab, "Cover Editor")
        self.tabs.addTab(self.header_footer_tab, "Header / Footer")
        self.tabs.addTab(self.live_preview_tab, "Live Preview")

        # Bottom status bar
        bottom = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        bottom.addWidget(self.status_label, stretch=1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        bottom.addWidget(self.progress_bar)

        self.build_button = QPushButton("BUILD PDF")
        self.build_button.setFixedHeight(40)
        self.build_button.clicked.connect(self.start_build)
        bottom.addWidget(self.build_button)

        layout.addLayout(bottom)

    def update_status(self, message: str):
        self.status_label.setText(message)
        QApplication.processEvents()

    def start_build(self):
        input_folder = self.main_tab.get_input_folder()
        output_file = self.main_tab.get_output_file()
        
        if not os.path.isdir(input_folder):
            QMessageBox.critical(self, "Error", self.config['static_strings']['error_invalid_folder'])
            return

        self.build_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.update_status(self.config['static_strings']['status_building'])

        self.build_thread = BuildThread(
            self.html_generator,
            self.pdf_renderer,
            input_folder,
            output_file
        )
        self.build_thread.progress_update.connect(self.update_status)
        self.build_thread.finished.connect(self.build_finished)
        self.build_thread.start()  # Direct QThread.start(), no QThreadPool

    def build_finished(self, success: bool, result: str):
        self.progress_bar.setVisible(False)
        self.build_button.setEnabled(True)
        
        if success:
            self.update_status(self.config['static_strings']['status_complete'])
            QMessageBox.information(self, "Success", self.config['static_strings']['success_pdf_built'])
            if QMessageBox.question(self, "", self.config['static_strings']['confirm_open_pdf']) == QMessageBox.StandardButton.Yes:
                self.open_file(result)
        else:
            self.update_status("Build failed")
            QMessageBox.critical(self, "Error", f"{self.config['static_strings']['error_build_failed']}: {result}")

    def open_file(self, path: str):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(("open", path))
            else:
                subprocess.call(("xdg-open", path))
        except Exception:
            QMessageBox.warning(self, "Warning", "Could not open file automatically.")

    def closeEvent(self, event):  # type: ignore[override]  # Pylance fix for parameter name mismatch
        if QMessageBox.question(self, "Exit", "Save configuration before exit?") == QMessageBox.StandardButton.Yes:
            self.config_manager.save_config()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()