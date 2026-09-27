"""Compatibility entry point for verified agent-run submission content."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('update_agent_content.py')), run_name='__main__')
