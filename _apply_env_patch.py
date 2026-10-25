# _apply_env_patch.py
from pathlib import Path

P = Path("execution/paper_position.py")
raw = P.read_text(encoding="utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
src = raw.replace("\r\n", "\n")

helpers = '''def _cfg_bool(key: str, default: bool) -> bool:
    for env_key in (f"PHOENIX_{key}", key):
        v = os.getenv(env_key)
        if v is not None:
            return v.strip().lower() in ("1", "true", "yes", "on")
    return bool(getattr(Settings, key, default))


def _cfg_float(key: str, default: float) -> float:
    for env_key in (f"PHOENIX_{key}", key):
        v = os.getenv(env_key)
        if v is not None:
            try:
                return float(v)
            except ValueError:
                pass
    return float(getattr(Settings, key, default))'''

reps = [
    ("    return float(table.get(order_type, 0.0))\n\n\n@dataclass",
     "    return float(table.get(order_type, 0.0))\n\n\n" + helpers + "\n\n\n@dataclass"),
    ('        if not getattr(Settings, "PARTIAL_TP_ENABLED", False):',
     '        if not _cfg_bool("PARTIAL_TP_ENABLED", False):'),
    ('        threshold = float(getattr(Settings, "PARTIAL_TP_AT_R", 1.0))',
     '        threshold = _cfg_float("PARTIAL_TP_AT_R", 1.0)'),
    ('            return float(getattr(Settings, "PARTIAL_TP_FRACTION", 0.5))',
     '            return _cfg_float("PARTIAL_TP_FRACTION", 0.5)'),
    ('        if getattr(Settings, "BE_ENABLED", False) and not self.be_moved:',
     '        if _cfg_bool("BE_ENABLED", False) and not self.be_moved:'),
    ('            be_at = float(getattr(Settings, "PARTIAL_TP_AT_R", 1.0))',
     '            be_at = _cfg_float("PARTIAL_TP_AT_R", 1.0)'),
    ('        if getattr(Settings, "TRAILING_ENABLED", False):',
     '        if _cfg_bool("TRAILING_ENABLED", False):'),
    ('            start_R = float(getattr(Settings, "TRAILING_START_R", 2.0))',
     '            start_R = _cfg_float("TRAILING_START_R", 2.0)'),
    ('                dist = float(getattr(Settings, "TRAILING_DISTANCE_R", 0.5))',
     '                dist = _cfg_float("TRAILING_DISTANCE_R", 0.5)'),
]

missing = [old for old, _ in reps if old not in src]
if missing:
    print(f"FAIL - {len(missing)} pattern(s) not found:")
    for m in missing:
        print(f"  {m!r}")
    raise SystemExit(1)

for old, new in reps:
    src = src.replace(old, new, 1)

with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src.replace("\n", nl))
print(f"OK - {len(reps)} replacements applied to {P}")