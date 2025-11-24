# Filename: src/html_generator.py
import re
import mistune
from pathlib import Path
from .config import ConfigManager
from .utils import discover_files

class HTMLGenerator:
    """Responsible for generating full HTML from Markdown files and configuration."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def _render_line_style(self, line: dict) -> str:
        style = (
            f'font-family: "{line["font"]}"; '
            f'font-size: {line["size"]}pt; '
            f'text-align: {line["align"]};'
        )
        if line.get("bold", False):
            style += " font-weight: bold;"
        if line.get("italic", False):
            style += " font-style: italic;"
        return style

    def generate_cover_html(self) -> str:
        cover_cover = self.config.config["cover"]
        lines = _cover.get("lines", [])
        bg_color = _cover.get("bg_color", "#0b2545")
        padding_top = _cover.get("padding_top", 180)

        lines_html = ""
        for line in lines:
            style = self._render_line_style(line)
            lines_html += f'<h1 style="{style}">{line["text"]}</h1>'

        return (
            f'<div class="cover-container" style="background: {bg_color}; '
            f'padding-top: {padding_top}pt; color: white; text-align: center; height: 100vh; '
            f'page-break-after: always;">{lines_html}</div>'
        )

    def _convert_md_to_html(self, md_content: str) -> str:
        md_content = re.sub(r'<!-- PAGEBREAK -->', '<div style="page-break-before: always;"></div>', md_content)
        renderer = mistune.HTMLRenderer()
        markdown = mistune.create_markdown(renderer=renderer)
        return markdown(md_content)  # type: ignore

    def generate_body_html(self, input_folder: str) -> str:
        files = discover_files(input_folder)
        body = ""
        for file in files:
            content = file.read_text(encoding="utf-8")
            body += self._convert_md_to_html(content)
            body += '<div style="page-break-before: always;"></div>'
        return body

    def generate_toc_html(self, body_html: str) -> str:
        headings = re.findall(r'<h([1-3]).*?id="([^"]*)".*?>(.*?)</h[1-3]>', body_html)
        if not headings:
            return '<div style="page-break-before: always;"></div>'

        toc = '<div id="toc" style="page-break-before: always;"><h1>Table of Contents</h1><ul>'
        for level, hid, text in headings:
            indent = "  " * (int(level) - 1)
            toc += f'<li style="margin-left: {int(level)-1}em;"><a href="#{hid}">{text}</a></li>'
        toc += '</ul></div>'
        return toc

    def generate_header_footer_html(self) -> tuple[str, str]:
        header_cfg = self.config.config.get("header", {})
        footer_cfg = self.config.config.get("footer", {})

        header_html = '<div id="header">'
        for line in header_cfg.get("lines", []):
            style = self._render_line_style(line)
            style += f" color: {header_cfg.get('color', '#000000')};"
            header_html += f'<p style="{style}">{line["text"]}</p>'
        header_html += '</div>'

        footer_html = '<div id="footer">'
        for line in footer_cfg.get("lines", []):
            text = line["text"].replace("{page}", '<span class="pageNumber"></span>')
            style = self._render_line_style(line)
            style += f" color: {footer_cfg.get('color', '#000000')};"
            footer_html += f'<p style="{style}">{text}</p>'
        footer_html += '</div>'

        return header_html, footer_html

    def generate_full_html(self, input_folder: str) -> str:
        cover = self.generate_cover_html()
        body = self.generate_body_html(input_folder)
        toc = self.generate_toc_html(body)
        header, footer = self.generate_header_footer_html()

        full_html = f"{header}{cover}{toc}{body}{footer}"
        return f"<html><body>{full_html}</body></html>"