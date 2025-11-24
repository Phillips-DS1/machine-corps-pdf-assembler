# Filename: src/config.py
import os
import re                      # <-- Added missing import
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Central configuration manager with runtime binding and persistence."""
    
    DEFAULTS = {
        'input_folder': 'inputs/',
        'output_file': 'machine_corps_policy_package.pdf',
        'classification': '',
        'use_latex_fallback': False,
        'cover': {
            'lines': [
                {'text': 'THE MACHINE CORPS INITIATIVE', 'align': 'center', 'font': 'Times New Roman', 'size': 56, 'bold': True, 'italic': False},
                {'text': 'COMPLETE POLICY PACKAGE', 'align': 'center', 'font': 'Times New Roman', 'size': 28, 'bold': False, 'italic': False},
                {'text': 'January 20, 2026', 'align': 'center', 'font': 'Times New Roman', 'size': 18, 'bold': False, 'italic': False}
            ],
            'bg_color': '#0b2545',
            'padding_top': 180
        },
        'header': {
            'lines': [{'text': 'The Machine Corps Initiative – Complete Policy Package', 'align': 'center', 'font': 'Times New Roman', 'size': 10, 'bold': False, 'italic': False}],
            'height': 20,
            'color': '#000000'
        },
        'footer': {
            'lines': [{'text': 'Page {page}', 'align': 'center', 'font': 'Times New Roman', 'size': 10, 'bold': False, 'italic': False}],
            'height': 20,
            'color': '#000000'
        },
        'static_strings': {
            'app_title': 'Machine Corps PDF Assembler – Presidential Briefing Book Tool',
            'status_ready': 'Ready – Load folder and click BUILD PDF',
            'status_building': 'Building PDF...',
            'status_complete': 'PDF build complete',
            'error_invalid_folder': 'Invalid input folder',
            'error_build_failed': 'Build failed',
            'success_pdf_built': 'PDF built successfully!',
            'confirm_open_pdf': 'Open the generated PDF now?'
        }
    }

    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load config from YAML with defaults and validation."""
        if not self.config_path.exists():
            logger.warning("config.yaml not found – creating with defaults")
            self.config = self.DEFAULTS.copy()
            self.save_config()
            return self.config

        with open(self.config_path, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f) or {}

        # Deep merge with defaults
        config = self.DEFAULTS.copy()
        for key, value in loaded.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                config[key] = {**config[key], **value}
            else:
                config[key] = value

        # Basic validation
        if not os.path.isdir(config['input_folder']):
            logger.warning("Invalid input_folder – resetting to default")
            config['input_folder'] = self.DEFAULTS['input_folder']

        self.config = config
        return config

    def save_config(self):
        """Persist configuration to YAML."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    def get(self, key: str, default=None):
        """Safe accessor for nested config values."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default if k == keys[-1] else {})
        return value

    def set(self, key: str, value):
        """Safe setter for nested config values."""
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def update_css_placeholders(self, css_content: str) -> str:
        """Apply current config values to CSS via string replacement."""
        header_height = str(self.config['header']['height'] + 20)
        footer_height = str(self.config['footer']['height'] + 20)
        cover_bg = self.config['cover']['bg_color']
        cover_padding = str(self.config['cover']['padding_top'])
        classification = self.config['classification']

        css_content = css_content.replace("margin-top: 20pt;", f"margin-top: {header_height}pt;")
        css_content = css_content.replace("margin-bottom: 20pt;", f"margin-bottom: {footer_height}pt;")
        css_content = css_content.replace("background: #0b2545;", f"background: {cover_bg};")
        css_content = css_content.replace("padding-top: 180pt;", f"padding-top: {cover_padding}pt;")

        if not classification:
            # Remove entire banner block when classification is empty
            css_content = re.sub(
                r'/\* Classification Banners.*?@page\s*\{.*?\}\s*\}\s*/\*\s*Table of Contents',
                '/* Table of Contents',
                css_content,
                flags=re.DOTALL
            )
        else:
            css_content = css_content.replace('content: "";', f'content: "{classification}";')

        return css_content