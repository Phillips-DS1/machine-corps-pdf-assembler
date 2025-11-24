# Filename: src/pdf_renderer.py
import os
import subprocess
import logging
from weasyprint import HTML, CSS
from .config import ConfigManager
from .utils import compute_hash

logger = logging.getLogger(__name__)

class PDFRenderer:
    """Handles PDF generation with WeasyPrint primary and Pandoc/LaTeX fallback."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def _load_base_css(self) -> str:
        """Load the base CSS file from resources."""
        css_path = os.path.join(os.path.dirname(__file__), 'resources', 'styles.txt')
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_render_css(self) -> str:
        """Apply current config overrides to base CSS."""
        base_css = self._load_base_css()
        return self.config.update_css_placeholders(base_css)

    def is_pandoc_available(self) -> bool:
        """Check if pandoc is installed."""
        try:
            subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def render_via_weasyprint(self, html_content: str, output_file: str) -> None:
        """Primary rendering path using WeasyPrint."""
        css_content = self.get_render_css()
        html = HTML(string=html_content)
        css = CSS(string=css_content)
        html.write_pdf(output_file, stylesheets=[css])
        logger.info("PDF rendered successfully with WeasyPrint")

    def render_via_pandoc_latex(self, html_content: str, output_file: str) -> None:
        """Fallback rendering using Pandoc → XeLaTeX."""
        if not self.is_pandoc_available():
            raise RuntimeError("Pandoc not available for LaTeX fallback")
        
        css_content = self.get_render_css()
        temp_html = 'temp.html'
        temp_css = 'temp.css'
        
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(f'<html><head><link rel="stylesheet" href="{temp_css}"></head><body>{html_content}</body></html>')
        with open(temp_css, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        cmd = [
            'pandoc', temp_html,
            '--pdf-engine=xelatex',
            '-o', output_file,
            '--css', temp_css,
            '--variable', 'geometry=letterpaper,margin=1in',
            '--variable', 'fontsize=12pt'
        ]
        subprocess.run(cmd, check=True)
        
        os.remove(temp_html)
        os.remove(temp_css)
        logger.info("PDF rendered successfully with Pandoc/LaTeX fallback")

    def render_pdf(self, html_content: str, output_file: str, progress_callback=None) -> None:
        """Main render method with fallback logic and progress."""
        if progress_callback:
            progress_callback("Rendering PDF...")
        try:
            if self.config.config.get('use_latex_fallback', False):
                raise Exception("LaTeX fallback forced via config")
            self.render_via_weasyprint(html_content, output_file)
        except Exception as e:
            logger.warning(f"WeasyPrint failed ({str(e)}); falling back to Pandoc/LaTeX")
            if progress_callback:
                progress_callback("Switching to LaTeX fallback...")
            self.render_via_pandoc_latex(html_content, output_file)
        
        pdf_hash = compute_hash(output_file)
        logger.info(f"PDF generated: {output_file} (SHA256: {pdf_hash})")
        if progress_callback:
            progress_callback("PDF build complete.")