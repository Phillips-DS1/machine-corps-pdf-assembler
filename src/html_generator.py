# Updated src/html_generator.py
import base64
import mistune
import re
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog
# ... existing code ...
class CustomRenderer(mistune.HTMLRenderer):
    """Custom renderer for advanced table formatting with ARIA."""
    def table(self, header, body):
        return f'<table role="table" aria-label="Data Table" class="custom-table" style="border: 1px solid; width: 100%;">{header}{body}</table>'

    def image(self, src, alt, title=None):
        return f'<img role="img" aria-label="{alt}" src="{src}" alt="{alt}"' + (f' title="{title}"' if title else '') + ' />'

# In HTMLGenerator:
def __init__(self, config_manager):
    self.config = config_manager
    self.markdown = mistune.create_markdown(renderer=CustomRenderer())

def _convert_md_to_html(self, md_content: str) -> str:
    md_content = re.sub(r'\[\[image:(\w+)\]\]', self.insert_image, md_content)
    md_content = re.sub(r'<!-- PAGEBREAK -->', '<div style="page-break-before: always;"></div>', md_content)
    return self.markdown(md_content)

def insert_image(self, match):
    """Handle image placeholder by prompting for file and embedding base64."""
    placeholder = match.group(1)
    file, _ = QFileDialog.getOpenFileName(None, f'Select Image for {placeholder}', '', 'Images (*.png *.jpg *.gif)')
    if not file:
        return f'<p>[Image placeholder: {placeholder}]</p>'
    with open(file, 'rb') as img_file:
        base64_img = base64.b64encode(img_file.read()).decode('utf-8')
        mime = 'image/png' if file.endswith('.png') else 'image/jpeg'  # Simplify
    return f'<img src="data:{mime};base64,{base64_img}" alt="{placeholder}">'