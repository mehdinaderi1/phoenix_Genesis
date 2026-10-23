"""
Shared JSONL persistence for intelligence memories.

- append-only (هر رکورد یک خط JSON)
- tolerance در برابر خطوط خراب (skip می‌کند، کرش نمی‌کند)
- reconstruct با __new__ + setattr (بدون وابستگی به __init__)
"""

import json
from pathlib import Path


def _safe(value, depth=0):
    """تبدیل هر آبجکت به ساختار JSON-safe."""
    if depth > 8:
        return str(value)

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {
            str(k): _safe(v, depth + 1)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_safe(v, depth + 1) for v in value]

    if hasattr(value, "__dataclass_fields__"):
        import dataclasses
        return _safe(dataclasses.asdict(value), depth + 1)

    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return _safe(value.to_dict(), depth + 1)
        except Exception:
            pass

    if hasattr(value, "__dict__"):
        return {
            str(k): _safe(v, depth + 1)
            for k, v in vars(value).items()
            if not str(k).startswith("_")
        }

    return str(value)


def append_record(path, record):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(_safe(record), ensure_ascii=False) + "\n")


def load_records(path):
    p = Path(path)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8-sig")
    records = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def reconstruct(cls, data, defaults=None):
    obj = cls.__new__(cls)
    for key, value in data.items():
        setattr(obj, key, value)
    if defaults:
        for key, default in defaults.items():
            if not hasattr(obj, key):
                setattr(obj, key, default)
    return obj