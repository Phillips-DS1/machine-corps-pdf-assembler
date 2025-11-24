# Filename: setup.py
from setuptools import setup, find_packages

setup(
    name="machine-corps-pdf-assembler",
    version="1.0.0",
    description="Presidential Briefing Book PDF Assembler – Machine Corps Initiative",
    author="Colin Gilchrist (AI Architect: Grok 4)",
    python_requires=">=3.12",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "src.resources": ["*.css", "*.txt"],
    },
    install_requires=[
        "weasyprint==62.2",
        "cssutils==2.11.1",
        "mistune==3.0.2",
        "PyYAML==6.0.2",
        "PyQt6==6.7.0",
        "PyQt6-WebEngine==6.7.0",
        "pytest==8.3.3",
    ],
    entry_points={
        "console_scripts": [
            "mc-assembler = src.gui.main_window:main",
        ]
    },
)