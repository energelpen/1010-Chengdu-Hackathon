#!/usr/bin/env python3
"""JSON CLI for Create Gmail draft; shared runtime enforces the schema and review policy."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from skill_runtime import cli
if __name__ == "__main__": cli("gmail-draft")
