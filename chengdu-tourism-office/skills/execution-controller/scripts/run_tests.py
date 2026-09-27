import runpy, sys
from pathlib import Path
root = Path(__file__).resolve().parents[3]
sys.argv = ["tourism_office.py", "test", Path(__file__).resolve().parents[1].name]
runpy.run_path(str(root / "scripts" / "tourism_office.py"), run_name="__main__")
