"""
tools/backup_state.py — Backup runner states with rotation

Copies futures + spot state files to data/backups/ with timestamp.
Keeps last 14 backups (7 days at 2x daily).

Usage:
    python tools/backup_state.py
"""
import os, shutil
from datetime import datetime

BACKUP_DIR = "data/backups"
KEEP_LAST = 14

FILES = [
    "data/futures_runner_state_dry.json",
    "data/spot_runner_state_dry.json",
]


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    for src in FILES:
        if not os.path.exists(src):
            print(f"[Skip] {src} (not found)")
            continue
        name = os.path.basename(src).replace(".json", "")
        dst = os.path.join(BACKUP_DIR, f"{name}_{ts}.json")
        shutil.copy2(src, dst)
        print(f"[OK] {src} -> {dst}")

    # Rotate: keep last KEEP_LAST per file
    for prefix in ["futures_runner_state_dry", "spot_runner_state_dry"]:
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith(prefix)],
            reverse=True,
        )
        for old in backups[KEEP_LAST:]:
            os.remove(os.path.join(BACKUP_DIR, old))
            print(f"[Rotate] removed {old}")

    print(f"\n[Done] backups in {BACKUP_DIR}")


if __name__ == "__main__":
    main()