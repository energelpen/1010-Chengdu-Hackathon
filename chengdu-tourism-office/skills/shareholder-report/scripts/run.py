import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/"scripts"))
from skill_runtime import cli
if __name__=="__main__": cli("shareholder-report")
