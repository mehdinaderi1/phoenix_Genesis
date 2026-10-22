from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone

from core.market_data.operational_action_translator import (
    OperationalActionTranslator
)
from core.market_data.operational_intelligence_adapter import (
    OperationalIntelligenceAdapter
)
from core.market_data.operational_intelligence_context_builder import (
    OperationalIntelligenceContextBuilder
)


class OperationalPaperRuntime:
    """Runs operational market data through intelligence and execution."""

    def __init__(
        self,
        market_context_runtime,
        intelligence_flow,
        paper_trading_runtime,
        session_archive=None,
        execution_runtime=None,
        shadow_execution_runtime=None,
        signal_publisher=None,
        opportunity_observer=None,
        opportunity_journal=None
    ):
        if market_context_runtime is None:
            raise ValueError(
                "market_context_runtime must not be None"
            )

        if intelligence_flow is None:
            raise ValueError(
                "intelligence_flow must not be None"
            )

        if paper_trading_runtime is None:
            raise ValueError(
                "paper_trading_runtime must not be None"
            )

        self.market_context_runtime = market_context_runtime
        self.intelligence_flow = intelligence_flow
        self.paper_trading_runtime = paper_trading_runtime
        self.execution_runtime = (
            execution_runtime
            if execution_runtime is not None
            else paper_trading_runtime
        )
        self.shadow_execution_runtime = (
            shadow_execution_runtime
        )
        self.session_archive = session_archive
        self.signal_publisher = signal_publisher
        self.opportunity_observer = opportunity_observer
        self.opportunity_journal = opportunity_journal

        self.context_builder = (
            OperationalIntelligenceContextBuilder()
        )

        self.adapter = OperationalIntelligenceAdapter()
        self.action_translator = OperationalActionTranslator()

    def run(
        self,
        symbol="BTCUSDT",
        cycles=1,
        continue_on_error=False,
        timeframes=None
    ):
        if cycles <= 0:
            raise ValueError(
                "cycles must be greater than zero"
            )

        results = []

        for cycle_number in range(1, cycles + 1):
            try:
                if timeframes is None:
                    cycle = self.market_context_runtime.run_cycle(
                        symbol=symbol
                    )
                else:
                    cycle = self.market_context_runtime.run_cycle(
                        symbol=symbol,
                        timeframes=timeframes
                    )

                candle_boundaries = cycle.get(
                    "candle_boundaries",
                    {}
                )

                observation = cycle["observation"]
                market_context = cycle["context"]

                if observation is None or market_context is None:
                    results.append({
                        "cycle_number": cycle_number,
                        "observation": observation,
                        "market_context": market_context,
                        "intelligence_context": None,
                        "report": None,
                        "decision": None,
                        "action_proposal": None,
                        "translated_action_proposal": None,
                        "paper_result": None,
                        "shadow_result": None,
                        "candle_boundaries": candle_boundaries,
                        "error": None
                    })
                    continue

                intelligence_context = (
                    self.context_builder.build(
                        market_context
                    )
                )

                consensus = self.adapter.to_consensus(
                    intelligence_context
                )

                candles = self._fetch_best_candles(symbol=symbol)

                report = self.intelligence_flow.create_report(
                    consensus,
                    candles=candles,
                )

                
                signal = str(
                    getattr(report, "signal", "") or ""
                ).upper()

                report.signal_timestamp = (
                    datetime.now(timezone.utc).isoformat()
                    if signal in {"BUY", "SELL"}
                    else None
                )

                translated_action_proposal = (
                    self.action_translator.translate(
                        report.action_proposal
                    )
                )
                opportunity = None
                opportunity_observation_error = None
                opportunity_journal_error = None

                if self.opportunity_observer is not None:
                    try:
                        opportunity = self.opportunity_observer.observe(
                            report,
                            decision=report.decision,
                            reference_price=observation.price,
                            symbol=observation.symbol,
                            observation_timestamp=getattr(
                                observation,
                                "timestamp",
                                None,
                            ),
                        )
                    except Exception as exc:
                        opportunity_observation_error = (
                            f"{type(exc).__name__}: {exc}"
                        )

                if (
                    opportunity is not None
                    and self.opportunity_journal is not None
                ):
                    try:
                        self.opportunity_journal.append(
                            self._serialize_value(opportunity)
                        )
                    except Exception as exc:
                        opportunity_journal_error = (
                            f"{type(exc).__name__}: {exc}"
                        )
                notification_error = None
                if self.signal_publisher is not None:
                    try:
                        self.signal_publisher.publish(
                            translated_action_proposal,
                            observation,
                            candle_boundaries,
                            generated_at=datetime.now(timezone.utc).isoformat(),
                        )
                    except Exception as exc:
                        notification_error = (
                            f"{type(exc).__name__}: {exc}"
                        )

                paper_input = {
                    "action_proposal": (
                        translated_action_proposal
                    ),
                    "price": observation.price,
                    "symbol": observation.symbol,
                    "decision": report.decision
                }

                execution_results = (
                    self.execution_runtime.run(
                        cycles=[paper_input],
                        symbol=symbol
                    )
                )

                paper_result = execution_results[0]

                shadow_result = None

                if self.shadow_execution_runtime is not None:
                    shadow_results = (
                        self.shadow_execution_runtime.run(
                            cycles=[paper_input],
                            symbol=symbol
                        )
                    )

                    shadow_result = shadow_results[0]

                results.append({
                    "cycle_number": cycle_number,
                    "observation": observation,
                    "market_context": market_context,
                    "intelligence_context": intelligence_context,
                    "report": report,
                    "decision": report.decision,
                    "action_proposal": report.action_proposal,
                    "translated_action_proposal": (
                        translated_action_proposal
                    ),
                    "paper_result": paper_result,
                    "shadow_result": shadow_result,
                    "candle_boundaries": candle_boundaries,
                    "notification_error": notification_error,
                    "opportunity": opportunity,
                    "opportunity_observation_error": (
                        opportunity_observation_error
                    ),
                    "opportunity_journal_error": (
                        opportunity_journal_error
                    ),
                    "error": None
                })

            except Exception as exc:
                if not continue_on_error:
                    raise

                results.append({
                    "cycle_number": cycle_number,
                    "observation": None,
                    "market_context": None,
                    "intelligence_context": None,
                    "report": None,
                    "decision": None,
                    "action_proposal": None,
                    "translated_action_proposal": None,
                    "paper_result": None,
                    "shadow_result": None,
                    "candle_boundaries": {},
                    "error": exc
                })

        return results

    def _fetch_candles(self, symbol, timeframe="30m", limit=250):
        """یک تایم‌فریم را از repository می‌خواند و به فرمت [ts,o,h,l,c,v] می‌دهد."""
        repo = getattr(self.market_context_runtime, "repository", None)
        if repo is None:
            return None

        rows = None

        # تلاش برای متدهای bulk رایج
        for name in ("get_candles", "get_recent_candles",
                     "fetch_candles", "list_candles",
                     "get_candles_range"):
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
                print(f"[CANDLES] {name} error: {e}")
                continue
            if rows:
                break

        # Fallback: SQL مستقیم
        if not rows:
            db = (getattr(repo, "database", None)
                  or getattr(repo, "db", None))
            if db is not None:
                try:
                    conn = (getattr(db, "connection", None)
                            or getattr(db, "conn", None)
                            or db)
                    cur = conn.execute(
                        "SELECT timestamp, open, high, low, close, volume "
                        "FROM market_candles "
                        "WHERE symbol=? AND timeframe=? "
                        "ORDER BY timestamp DESC LIMIT ?",
                        (symbol, timeframe, limit),
                    )
                    rows = list(cur.fetchall())[::-1]
                except Exception as e:
                    print(f"[CANDLES] sql fallback error: {e}")
                    return None

        if not rows:
            return None

        # یکسان‌سازی به [ts, o, h, l, c, v]
        result = []
        for r in rows:
            if isinstance(r, dict):
                result.append([
                    r.get("timestamp"), r.get("open"), r.get("high"),
                    r.get("low"), r.get("close"), r.get("volume"),
                ])
            elif isinstance(r, (list, tuple)):
                if len(r) >= 9:  # full DB row
                    result.append([r[3], r[4], r[5], r[6], r[7], r[8]])
                elif len(r) >= 6:
                    result.append([r[0], r[1], r[2], r[3], r[4], r[5]])

        if not result:
            return None
        print(f"[CANDLES] {len(result)} candles for {symbol} {timeframe}")
        return result

    def _fetch_best_candles(self, symbol, limit=250):
        """اولین تایم‌فریمی که ≥۲۰۰ کندل دارد را برمی‌گرداند."""
        for tf in ("30m", "15m", "5m", "4H", "1D"):
            candles = self._fetch_candles(symbol, tf, limit)
            if candles and len(candles) >= 200:
                return candles
        # fallback: هرچه داشت
        for tf in ("30m", "15m", "5m"):
            candles = self._fetch_candles(symbol, tf, limit)
            if candles:
                return candles
        return None

    @staticmethod
    def _serialize_value(value):
        if value is None:
            return None

        if is_dataclass(value):
            return OperationalPaperRuntime._serialize_value(
                asdict(value)
            )

        if isinstance(value, dict):
            return {
                str(key): OperationalPaperRuntime._serialize_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                OperationalPaperRuntime._serialize_value(
                    item
                )
                for item in value
            ]

        if isinstance(value, (str, int, float, bool)):
            return value

        if hasattr(value, "__dict__"):
            return {
                str(key): OperationalPaperRuntime._serialize_value(
                    item
                )
                for key, item in vars(value).items()
            }

        return str(value)

    def _build_session_record(self, results):
        summary = self.build_summary(results)
        serializable_summary = self._serialize_value(summary)

        cycles = []

        for result in results:
            paper_result = result.get("paper_result")
            recovery_result = result.get("recovery_result")

            # ✱ NEW: مسیر recovery (خارج از observation cycle)
            if paper_result is None and recovery_result is not None:
                rr = recovery_result
                pos = rr.get("position")
                cycles.append({
                    "cycle": result.get("cycle_number"),
                    "symbol": getattr(pos, "symbol", "BTCUSDT") if pos else "BTCUSDT",
                    "price": rr.get("exit_price"),
                    "timestamp": None,
                    "source_status": None,
                    "fallback_used": None,
                    "consensus_breakdown": None,
                    "signal": None,
                    "trend": None,
                    "regime": None,
                    "confidence": None,
                    "risk": None,
                    "proposal_action": None,
                    "proposal_status": None,
                    "proposal_reason": None,
                    "action": "RECOVERY_CLOSE",
                    "execution_status": "CLOSED",
                    "realized_pnl": rr.get("realized_pnl", 0.0),
                    "position_side": getattr(pos, "side", None) if pos else None,
                    "entry_price": getattr(pos, "entry_price", None) if pos else None,
                    "quantity": getattr(pos, "quantity", None) if pos else None,
                    "leverage": float(getattr(pos, "leverage", 1.0)) if pos else 1.0,
                    "opportunity": None,
                    "opportunity_observation_error": None,
                    "error": None,
                })
                continue

            # مسیر معمولی (paper_result)
            observation = result.get("observation")
            market_context = result.get("market_context")
            report = result.get("report")
            action_proposal = result.get("action_proposal")

            cycles.append({
                "cycle": result.get("cycle_number"),
                "symbol": getattr(observation, "symbol", None),
                "price": getattr(observation, "price", None),
                "timestamp": getattr(observation, "timestamp", None),
                "source_status": getattr(observation, "source_status", None),
                "fallback_used": getattr(observation, "fallback_used", None),
                "consensus_breakdown": self._serialize_value(
                    getattr(market_context, "consensus_breakdown", None)
                ),
                "signal": getattr(report, "signal", None),
                "trend": getattr(report, "trend", None),
                "regime": getattr(report, "regime", None),
                "confidence": getattr(report, "confidence", None),
                "risk": getattr(report, "risk", None),
                "proposal_action": getattr(action_proposal, "action", None),
                "proposal_status": getattr(action_proposal, "status", None),
                "proposal_reason": getattr(action_proposal, "reason", None),
                "action": paper_result.get("action") if paper_result is not None else None,
                "execution_status": (
                    getattr(paper_result.get("execution_result"), "status", None)
                    if paper_result is not None else None
                ),
                "realized_pnl": (
                    paper_result.get("realized_pnl", 0.0)
                    if paper_result is not None else None
                ),
                "position_side": getattr(
                    paper_result.get("position") if paper_result is not None else None,
                    "side", None,
                ),
                "entry_price": getattr(
                    paper_result.get("position") if paper_result is not None else None,
                    "entry_price", None,
                ),
                "quantity": getattr(
                    paper_result.get("position") if paper_result is not None else None,
                    "quantity", None,
                ),
                "leverage": float(getattr(
                    paper_result.get("position") if paper_result is not None else None,
                    "leverage", 1.0,
                )),
                "opportunity": self._serialize_value(result.get("opportunity")),
                "opportunity_observation_error": result.get("opportunity_observation_error"),
                "error": (
                    str(result["error"])
                    if result.get("error") is not None
                    else None
                ),
            })
        
        return {
            "session_id": self.paper_trading_runtime.session.session_id,
            "cycles": cycles,
            "summary": serializable_summary,
            "final_position": self._serialize_value(summary.get("current_position")),
        }

    def _archive_session(self, results):
        if self.session_archive is None:
            return None

        session_record = self._build_session_record(
            results
        )

        self.session_archive.save(
            self.paper_trading_runtime.session.session_id,
            session_record
        )

        return session_record

    def archive_results(self, results):
        return self._archive_session(results)

    def build_summary(self, results):
        if results is None:
            raise ValueError(
                "results must not be None"
            )

        paper_results = [
            result["paper_result"]
            for result in results
            if result.get("paper_result") is not None
        ]

        summary = self.paper_trading_runtime.build_summary(
            paper_results
        )
         # SL/TP closes not counted in results → use trade_history
        trade_history_closes = (
            self.paper_trading_runtime.session.get_trade_count()
            - summary.get("trade_count", 0)
        )

        
        if trade_history_closes > 0:
            summary["close_count"] = summary.get("close_count", 0) + trade_history_closes

        
        blind_cycles = sum(
            1
            for result in results
            if (
                result.get("observation") is not None
                and result.get("observation").source_status == "BLIND"
            )
        )

        error_cycles = sum(
            1
            for result in results
            if result.get("error") is not None
        )

        no_data_cycles = sum(
            1
            for result in results
            if (
                result.get("error") is None
                and not (
                    result.get("observation") is not None
                    and result.get("observation").source_status == "BLIND"
                )
                and (
                    result.get("observation") is None
                    or result.get("market_context") is None
                )
            )
        )
        summary["cycles_processed"] = len(results)
        summary["successful_cycles"] = len(paper_results)
        summary["blind_cycles"] = blind_cycles
        summary["no_data_cycles"] = no_data_cycles
        summary["error_cycles"] = error_cycles

        return summary

