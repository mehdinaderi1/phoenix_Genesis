from core.market_data.repository import MarketDataRepository
from time import time


class SourceCandlePipeline:
    """Fetches candles through the market-data source manager and stores them."""

    def __init__(self, source_manager, database):
        if source_manager is None:
            raise ValueError("source_manager must not be None")
        if database is None:
            raise ValueError("database must not be None")

        self.source_manager = source_manager
        self.repository = MarketDataRepository(database)
        # TTL cache: skip fetch if recently fetched
        self._last_fetch = {}
        self._candle_ttl = {
            "1m": 20, "5m": 100, "15m": 300, "30m": 600,
            "1H": 1200, "4H": 4800, "1D": 28800,
        }

    def _ordered_source_names(self):
        ordered_names = []
        if self.source_manager.primary_source:
            ordered_names.append(self.source_manager.primary_source)
        ordered_names.extend(
            name
            for name in self.source_manager.sources
            if name != self.source_manager.primary_source
        )
        return ordered_names

    def _health(self, name, _health_cache):
        source = self.source_manager.sources[name]
        if _health_cache is not None and name in _health_cache:
            return _health_cache[name]
        healthy = source.health_check()
        if _health_cache is not None:
            _health_cache[name] = healthy
        return healthy

    def fetch_and_store(
        self,
        symbol="BTCUSDT",
        timeframe="1m",
        _health_cache=None
    ):
        if not symbol:
            raise ValueError("symbol must not be empty")

        # ─── TTL cache check ───
        cache_key = (symbol, timeframe)
        ttl = self._candle_ttl.get(timeframe, 60)
        now = time()
        last = self._last_fetch.get(cache_key, 0)

        if now - last < ttl:
            latest_row = self.repository.get_latest_candle(symbol, timeframe)
            if latest_row is not None:
                return {
                    "stored": False,
                    "source": "cache",
                    "candle": {
                        "timestamp": latest_row[3],
                        "open": latest_row[4],
                        "high": latest_row[5],
                        "low": latest_row[6],
                        "close": latest_row[7],
                        "volume": latest_row[8],
                    },
                    "cached": True,
                    "age_seconds": now - last,
                }
        # ─── END cache check ───

        for name in self._ordered_source_names():
            try:
                if not self._health(name, _health_cache):
                    continue
                candle = self.source_manager.sources[name].get_candle(
                    symbol, timeframe
                )
            except Exception:
                continue

            if candle is None:
                continue

            saved = self.repository.save_candle(
                symbol,
                timeframe,
                candle["open"],
                candle["high"],
                candle["low"],
                candle["close"],
                candle["volume"],
                candle["timestamp"],
            )

            self._last_fetch[cache_key] = now

            return {
                "stored": bool(saved),
                "source": name,
                "candle": candle,
                "cached": False,
            }

        return {
            "stored": False,
            "source": None,
            "candle": None,
            "cached": False,
        }

    def fetch_and_store_historical(
        self,
        symbol="BTCUSDT",
        timeframe="1m",
        limit=30,
        _health_cache=None
    ):
        if not symbol:
            raise ValueError("symbol must not be empty")

        if limit <= 0:
            return {
                "source": None,
                "fetched": 0,
                "stored": 0
            }

        for name in self._ordered_source_names():
            try:
                if not self._health(name, _health_cache):
                    continue
                candles = self.source_manager.sources[name].get_historical_candles(
                    symbol, timeframe, limit
                )
            except Exception:
                continue

            if not candles:
                continue

            stored_count = 0
            for candle in candles:
                saved = self.repository.save_candle(
                    symbol,
                    timeframe,
                    candle["open"],
                    candle["high"],
                    candle["low"],
                    candle["close"],
                    candle["volume"],
                    candle["timestamp"],
                )
                if saved:
                    stored_count += 1

            return {
                "source": name,
                "fetched": len(candles),
                "stored": stored_count
            }

        return {
            "source": None,
            "fetched": 0,
            "stored": 0
        }

    def warm_up(
        self,
        symbol="BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D"),
        limit=30
    ):
        results = {}
        health_cache = {}

        for timeframe in timeframes:
            results[timeframe] = self.fetch_and_store_historical(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                _health_cache=health_cache
            )

        return results