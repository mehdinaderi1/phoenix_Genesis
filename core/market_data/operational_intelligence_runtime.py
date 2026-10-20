from core.market_data.operational_intelligence_adapter import (
    OperationalIntelligenceAdapter
)
from core.market_data.operational_intelligence_context_builder import (
    OperationalIntelligenceContextBuilder
)


class OperationalIntelligenceRuntime:
    """Runs operational market context through Phoenix intelligence."""

    def __init__(self, market_context_runtime, intelligence_flow):
        if market_context_runtime is None:
            raise ValueError("market_context_runtime must not be None")
        if intelligence_flow is None:
            raise ValueError("intelligence_flow must not be None")

        self.market_context_runtime = market_context_runtime
        self.intelligence_flow = intelligence_flow
        self.context_builder = OperationalIntelligenceContextBuilder()
        self.adapter = OperationalIntelligenceAdapter()

    def _normalize_row(self, r):
        """DB row یا dict را به dict با close تبدیل کن"""
        if isinstance(r, dict):
            return r
        if isinstance(r, (list, tuple)):
            # DB full row: (id, symbol, tf, ts, o, h, l, c, v, created_at)
            if len(r) >= 9:
                return {
                    "timestamp": r[3],
                    "open": r[4], "high": r[5], "low": r[6],
                    "close": r[7], "volume": r[8],
                }
            # 6-tuple: (ts, o, h, l, c, v)
            if len(r) >= 6:
                return {
                    "timestamp": r[0],
                    "open": r[1], "high": r[2], "low": r[3],
                    "close": r[4], "volume": r[5],
                }
        return None

    def _fetch_candles(self, symbol, timeframe="5m", limit=250):
        """کندل‌ها را از repository بگیر و به فرمت trend_filter تبدیل کن."""
        repo = getattr(self.market_context_runtime, "repository", None)
        if repo is None:
            return None

        rows = None

        # تلاش برای متدهای bulk رایج
        for name in ("get_candles", "get_recent_candles",
                     "fetch_candles", "list_candles",
                     "get_candles_range", "get_candles_for"):
            method = getattr(repo, name, None)
            if method is None:
                continue
            try:
                rows = method(symbol, timeframe, limit=limit)
            except TypeError:
                try:
                    rows = method(symbol, timeframe)
                except Exception:
                    continue
            except Exception as e:
                print(f"[CANDLES] {name} failed: {e}")
                continue
            if rows:
                break

        # Fallback: SQL مستقیم روی DB
        if not rows:
            db = getattr(repo, "database", None) or getattr(repo, "db", None)
            if db is not None:
                try:
                    conn = (
                        getattr(db, "connection", None)
                        or getattr(db, "conn", None)
                        or db
                    )
                    cur = conn.execute(
                        "SELECT id, symbol, timeframe, timestamp, "
                        "open, high, low, close, volume, created_at "
                        "FROM market_candles "
                        "WHERE symbol=? AND timeframe=? "
                        "ORDER BY timestamp DESC LIMIT ?",
                        (symbol, timeframe, limit),
                    )
                    rows = list(cur.fetchall())[::-1]
                except Exception as e:
                    print(f"[CANDLES] sql fallback failed: {e}")

        if not rows:
            print(f"[CANDLES] no rows for {symbol} {timeframe}")
            return None

        normalized = [self._normalize_row(r) for r in rows]
        normalized = [c for c in normalized if c]
        print(f"[CANDLES] fetched {len(normalized)} for {symbol} {timeframe}")
        return normalized

    def run(self, symbol="BTCUSDT", cycles=1):
        contexts = self.market_context_runtime.run(
            symbol=symbol,
            cycles=cycles
        )

        results = []

        for market_context in contexts:
            intelligence_context = self.context_builder.build(
                market_context
            )

            consensus = self.adapter.to_consensus(
                intelligence_context
            )

            # ─── کندل‌ها برای فیلتر EMA ───
            candles = self._fetch_candles(
                symbol=symbol,
                timeframe="5m",
                limit=250,
            )
            # ─────────────────────────────

            report = self.intelligence_flow.create_report(
                consensus,
                candles=candles,
            )

            results.append({
                "market_context": market_context,
                "intelligence_context": intelligence_context,
                "report": report,
                "decision": report.decision,
                "action_proposal": report.action_proposal
            })

        return results