"""
Probe XTExchange internals to understand auth + request pattern.
Read-only, no side effects.
"""
import sys
import inspect
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from exchanges.xt_exchange import XTExchange

xt = XTExchange(timeout=10)

print("=" * 70)
print("BASE_URL")
print("=" * 70)
print(xt.BASE_URL)
print()

print("=" * 70)
print("_request source")
print("=" * 70)
print(inspect.getsource(xt._request))
print()

print("=" * 70)
print("connect / __init__ source")
print("=" * 70)
try:
    print(inspect.getsource(XTExchange.__init__))
except Exception as e:
    print(f"cannot inspect: {e}")
print()

print("=" * 70)
print("get_balance source")
print("=" * 70)
try:
    print(inspect.getsource(xt.get_balance))
except Exception as e:
    print(f"cannot inspect: {e}")
print()

print("=" * 70)
print("TIMEFRAME_MAP")
print("=" * 70)
print(xt.TIMEFRAME_MAP)