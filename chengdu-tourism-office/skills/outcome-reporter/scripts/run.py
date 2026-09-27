import runpy, sys
from pathlib import Path
root = Path(__file__).resolve().parents[3]
sys.argv = ["tourism_office.py", "run", Path(__file__).resolve().parents[1].name, *sys.argv[1:]]
runpy.run_path(str(root / "scripts" / "tourism_office.py"), run_name="__main__")
