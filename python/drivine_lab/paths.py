from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
CONCEPTS_PATH = DATA_DIR / "concepts.json"
INSTRUCT_PATH = DATA_DIR / "drivine_instruct.json"
PROFILES_PATH = DATA_DIR / "amd_profiles.json"
DEFAULT_GRAPH_DB = DATA_DIR / "drivine_lab.db"
DEFAULT_JSONL = DATA_DIR / "drivine_instruct.jsonl"
