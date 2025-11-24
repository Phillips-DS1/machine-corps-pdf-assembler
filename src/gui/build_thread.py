# Filename: src/gui/build_thread.py
from PyQt6.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class BuildThread(QThread):
    """Non-blocking thread for PDF generation with progress and completion signals."""
    
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message/path or error
    
    def __init__(self, html_generator, pdf_renderer, input_folder: str, output_file: str):
        super().__init__()
        self.html_generator = html_generator
        self.pdf_renderer = pdf_renderer
        self.input_folder = input_folder
        self.output_file = output_file

    def run(self):
        try:
            self.progress_update.emit("Generating HTML content...")
            html_content = self.html_generator.generate_full_html(self.input_folder)
            
            self.progress_update.emit("Rendering PDF...")
            self.pdf_renderer.render_pdf(html_content, self.output_file, self.progress_update.emit)
            
            self.finished.emit(True, self.output_file)
        except Exception as e:
            logger.error(f"Build failed in thread: {e}")
            self.finished.emit(False, str(e))