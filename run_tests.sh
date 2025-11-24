# Filename: run_tests.sh
#!/bin/bash
pytest tests/ -v --cov=src --cov-report=html
open htmlcov/index.html  # macOS/Linux; for Windows use start htmlcov\index.html