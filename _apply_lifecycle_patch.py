from pathlib import Path

P = Path("execution/paper_position_lifecycle.py")
raw = P.read_text(encoding="utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
src = raw.replace("\r\n", "\n")

reps = [
    # helper import
    ("from config.settings import Settings\n",
     "from config.settings import Settings\nfrom execution.paper_position import _cfg_bool, _cfg_float\n"),
    # inner PARTIAL_TP_ENABLED check
    ('                    if getattr(Settings, "PARTIAL_TP_ENABLED", False):',
     '                    if _cfg_bool("PARTIAL_TP_ENABLED", False):'),
    # TP_EXTEND_AFTER_PARTIAL_R
    ('                        extend_R = float(\n                            getattr(Settings, "TP_EXTEND_AFTER_PARTIAL_R", 3.0)\n                        )',
     '                        extend_R = _cfg_float(\n                            "TP_EXTEND_AFTER_PARTIAL_R", 3.0\n                        )'),
]

for old, new in reps:
    if old not in src:
        print(f"FAIL - pattern not found: {old[:70]!r}...")
        raise SystemExit(1)
    src = src.replace(old, new, 1)

with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src.replace("\n", nl))
print(f"OK - {len(reps)} replacements applied to {P}")