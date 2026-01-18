#!/usr/bin/env python
"""
Wrapper script to run Streamlit app properly
Run this from project root
"""

import subprocess
import sys
from pathlib import Path

# Change to src directory
src_path = Path(__file__).parent / "src"

# Run streamlit from project root with proper Python path
result = subprocess.run(
    [sys.executable, "-m", "streamlit", "run", str(src_path / "app.py")],
    cwd=str(Path(__file__).parent)
)

sys.exit(result.returncode)
