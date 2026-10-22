from pathlib import Path
import logging

from execution.paper_session_store import (
    PaperSessionStore
)

logger = logging.getLogger(__name__)


class PaperSessionArchive:

    def __init__(
        self,
        root_path,
        store=None
    ):
        self.root_path = Path(
            root_path
        )

        self.store = (
            store
            or PaperSessionStore()
        )

        self.root_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(
        self,
        session_id,
        session_record
    ):
        path = self.root_path / (
            f"{session_id}.json"
        )

        # ✱ merge با archive موجود تا cycleهای قبلی حفظ شوند
        if path.exists():
            try:
                existing = self.store.load(path)
                session_record = self._merge_records(
                    existing, session_record
                )
            except Exception as exc:
                logger.warning(
                    "Could not merge existing archive %s: %s",
                    path, exc,
                )

        self.store.save(
            session_record,
            path
        )

    def _merge_records(self, existing, new):
        """ادغام run جدید در archive تجمعی."""
        merged = dict(new)

        existing_cycles = existing.get("cycles") or []
        new_cycles = new.get("cycles") or []

        # ایندکس cycle_numberهای موجود (فقط cycle > 0)
        by_number = {}
        merged_cycles = list(existing_cycles)
        for idx, c in enumerate(merged_cycles):
            cn = c.get("cycle")
            if cn is not None and cn > 0:
                by_number[cn] = idx

        # append یا replace
        for c in new_cycles:
            cn = c.get("cycle")
            if cn is not None and cn > 0 and cn in by_number:
                # جایگزینی cycle تکراری (مثلاً RESUME از همان شماره)
                merged_cycles[by_number[cn]] = c
            else:
                merged_cycles.append(c)
                if cn is not None and cn > 0:
                    by_number[cn] = len(merged_cycles) - 1

        merged["cycles"] = merged_cycles

        # به‌روزرسانی summary تجمعی
        summary = dict(merged.get("summary") or {})
        summary["cycles_processed"] = len(merged_cycles)

        # reconciliation
        sum_realized = sum(
            (c.get("realized_pnl") or 0.0)
            for c in merged_cycles
        )
        total_pnl = summary.get("total_pnl", 0.0)
        delta = total_pnl - sum_realized

        summary["pnl_reconcile_delta"] = delta
        summary["pnl_reconciled"] = abs(delta) < 1e-6

        if abs(delta) > 1e-6:
            logger.warning(
                "PnL reconciliation mismatch: "
                "total_pnl=%.10f sum_cycles=%.10f delta=%+.10f",
                total_pnl, sum_realized, delta,
            )

        merged["summary"] = summary
        return merged

    def load(
        self,
        session_id
    ):
        path = self.root_path / (
            f"{session_id}.json"
        )

        return self.store.load(
            path
        )

    def list(
        self
    ):
        return sorted(
            path.stem
            for path in self.root_path.glob("*.json")
            if not path.name.endswith(".checkpoint.json")
        )