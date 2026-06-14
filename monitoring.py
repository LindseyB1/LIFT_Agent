from difflib import SequenceMatcher
from datetime import datetime
from pathlib import Path
import json

MONITORING_DIR = Path("Monitoring")
MONITORING_DIR.mkdir(exist_ok=True)


def compare_text_changes(previous_text, updated_text):
    previous = str(previous_text or "").strip()
    updated = str(updated_text or "").strip()

    similarity = SequenceMatcher(None, previous, updated).ratio()
    changed = previous != updated
    meaningful_change = changed and similarity < 0.92

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "changed": changed,
        "meaningful_change": meaningful_change,
        "similarity_score": round(similarity, 3),
        "previous_length": len(previous),
        "updated_length": len(updated),
    }


def save_monitoring_result(result):
    path = MONITORING_DIR / "monitoring_results.jsonl"
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(result) + "\n")
    return path
