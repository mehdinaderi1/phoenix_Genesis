import os


class DecisionRules:
    """
    Decision gating rules for LONG/SHORT.

    Feature flag: PHOENIX_RELAXED_RULES

    Legacy mode (default):
      - CONSENSUS_MIN_CONFIDENCE = 0.6
      - LONG: signal==BUY, risk==LOW, confidence>=80
      - SHORT: signal==SELL, confidence>=70
      - Circular dependency: signal must equal consensus decision

    Relaxed mode (flag on):
      - CONSENSUS_MIN_CONFIDENCE = 0.4
      - LONG: signal in (BUY, WAIT), risk in (LOW, MEDIUM), confidence>=60
      - SHORT: signal in (SELL, WAIT), confidence>=50
      - Circular dependency removed (WAIT allowed)
    """

    USE_RELAXED_RULES = (
        os.getenv("PHOENIX_RELAXED_RULES", "0").strip() == "1"
    )

    # ─────────────────────────────────────────────────────────
    # آستانه‌ی اجماع
    # ─────────────────────────────────────────────────────────
    CONSENSUS_MIN_CONFIDENCE = float(os.getenv(
        "PHOENIX_CONSENSUS_MIN_CONFIDENCE",
        "0.4" if USE_RELAXED_RULES else "0.6"
    ))

    # ─────────────────────────────────────────────────────────
    # آستانه‌های Confidence
    # ─────────────────────────────────────────────────────────
    LONG_MIN_CONFIDENCE = 30 if USE_RELAXED_RULES else 80
    SHORT_MIN_CONFIDENCE = 20 if USE_RELAXED_RULES else 70

    # ─────────────────────────────────────────────────────────
    # Risk مجاز برای LONG
    # ─────────────────────────────────────────────────────────
    _ALLOW_HIGH = os.getenv("PHOENIX_ALLOW_HIGH_RISK", "0").strip() == "1"
    LONG_ALLOWED_RISK = (
        (("LOW", "MEDIUM", "HIGH") if _ALLOW_HIGH else ("LOW", "MEDIUM"))
        if USE_RELAXED_RULES else ("LOW",)
    )
    # Risk مجاز برای SHORT (هم‌سیاست با LONG)
    SHORT_ALLOWED_RISK = LONG_ALLOWED_RISK

    # ─────────────────────────────────────────────────────────
    # سیگنال‌های مجاز
    # ─────────────────────────────────────────────────────────
    LONG_ALLOWED_SIGNALS = (
        ("BUY", "WAIT") if USE_RELAXED_RULES else ("BUY",)
    )
    SHORT_ALLOWED_SIGNALS = (
        ("SELL", "WAIT") if USE_RELAXED_RULES else ("SELL",)
    )

    # =========================================================
    # اعتبارسنجی استراتژی
    # =========================================================

    def strategy_is_valid(self, report):

        strategy = getattr(report, "champion_strategy", None)

        if strategy is None:
            return True

        return strategy.get("status") == "ACTIVE"

    # =========================================================
    # اعتبارسنجی اجماع
    # =========================================================

    def consensus_is_valid(self, report):

        consensus = getattr(report, "strategy_consensus", None)

        if consensus is None:
            return True

        decision = consensus.get("decision")

        if decision not in ["BUY", "SELL"]:
            return False

        report_signal = getattr(report, "signal", None)

        if self.USE_RELAXED_RULES:
            # در حالت relaxed، اگر signal=WAIT باشد، چک تطابق
            # انجام نمی‌شود. این حلقه‌ی بسته را می‌شکند.
            if (
                report_signal is not None
                and report_signal != "WAIT"
                and decision != report_signal
            ):
                return False
        else:
            # رفتار قدیمی: تطابق دقیق
            if (
                report_signal is not None
                and decision != report_signal
            ):
                return False

        supporting = consensus.get("supporting_strategies", 0)
        opposing = consensus.get(
            "opposing_strategies",
            consensus.get("consensus_confidence", 0),
        )

        if supporting <= opposing:
            return False

        confidence = consensus.get("confidence", 0)

        if confidence < self.CONSENSUS_MIN_CONFIDENCE:
            return False

        return True

    # =========================================================
    # گیت LONG
    # =========================================================

    def can_long(self, report):

        signal = getattr(report, "signal", None)
        risk = getattr(report, "risk", None)
        confidence = getattr(report, "confidence", 0)

        return (
            self.strategy_is_valid(report)
            and self.consensus_is_valid(report)
            and signal in self.LONG_ALLOWED_SIGNALS
            and risk in self.LONG_ALLOWED_RISK
            and confidence >= self.LONG_MIN_CONFIDENCE
        )

    # =========================================================
    # گیت SHORT
    # =========================================================

    def can_short(self, report):

        signal = getattr(report, "signal", None)
        risk = getattr(report, "risk", None)
        confidence = getattr(report, "confidence", 0)

        return (
            self.strategy_is_valid(report)
            and self.consensus_is_valid(report)
            and signal == "SELL"
            and risk in self.SHORT_ALLOWED_RISK
            and confidence >= self.SHORT_MIN_CONFIDENCE
        )
        
    def diagnose_long(self, report):
        """Return (allowed: bool, reason_code: str | None)."""
        if not self.strategy_is_valid(report):
            return False, "DECISION_STRATEGY_BLOCKED"

        if not self.consensus_is_valid(report):
            return False, "CONSENSUS_INVALID_DECISION"

        signal = getattr(report, "signal", None)
        if signal not in self.LONG_ALLOWED_SIGNALS:
            return False, "DECISION_SIGNAL_INVALID"

        risk = getattr(report, "risk", None)
        if risk not in self.LONG_ALLOWED_RISK:
            return False, "DECISION_RISK_HIGH"

        conf = getattr(report, "confidence", 0)
        if conf < self.LONG_MIN_CONFIDENCE:
            return False, (
                f"DECISION_CONFIDENCE_LOW: "
                f"{conf:.1f} < {self.LONG_MIN_CONFIDENCE}"
            )

        return True, None

    def diagnose_short(self, report):
        """Return (allowed: bool, reason_code: str | None)."""
        if not self.strategy_is_valid(report):
            return False, "DECISION_STRATEGY_BLOCKED"

        if not self.consensus_is_valid(report):
            return False, "CONSENSUS_INVALID_DECISION"

        signal = getattr(report, "signal", None)
        if signal not in self.SHORT_ALLOWED_SIGNALS:
            return False, "DECISION_SIGNAL_INVALID"

        risk = getattr(report, "risk", None)
        if risk not in self.SHORT_ALLOWED_RISK:
            return False, "DECISION_RISK_HIGH"

        conf = getattr(report, "confidence", 0)
        if conf < self.SHORT_MIN_CONFIDENCE:
            return False, (
                f"DECISION_CONFIDENCE_LOW: "
                f"{conf:.1f} < {self.SHORT_MIN_CONFIDENCE}"
            )

        return True, None