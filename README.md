# Filename: README.md

# Machine Corps PDF Assembler

## Overview
This tool assembles Markdown files into a professional PDF briefing book for the Machine Corps Initiative. It features a PyQt6 GUI for configuration, live previews, automatic TOC generation, classification banners, and deterministic output. Primary rendering uses WeasyPrint; fallback to Pandoc/LaTeX for advanced typography.

## Installation
1. Install dependencies: `pip install -r requirements.txt`
2. Install as editable package: `pip install -e .`
3. (Optional) Install Pandoc from https://pandoc.org for LaTeX fallback.

## Usage
- Run: `python src/gui/main_window.py` or use launch.bat/sh.
- Configure via GUI tabs: Input/Output, Cover, Header/Footer.
- Click "Update CSS" in tabs to apply overrides and refresh preview.
- "Save as Default" persists changes to config.yaml.
- Build PDF for output.

## Testing
Run tests: `pytest tests/` or use run_tests.sh.

## Architecture
- `src/config.py`: Config loading and CSS overriding.
- `src/utils.py`: File utilities.
- `src/html_generator.py`: HTML assembly.
- `src/pdf_renderer.py`: PDF rendering with fallback.
- `src/gui/*`: PyQt6 UI components.
- `resources/styles.css`: Base CSS with placeholders.

For issues, contact Colin Gilchrist.