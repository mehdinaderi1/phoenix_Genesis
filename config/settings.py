class Settings:
    """??????? ???? ????? ?????"""

    APP_NAME = "Phoenix Genesis"
    VERSION = "0.1.0"

    DEBUG = True

    DATA_PATH = "data"
    LOG_PATH = "logs"
    BACKUP_PATH = "backup"

    DEFAULT_EXCHANGE = "XT"

    DEMO_MODE = True
    REAL_EXECUTION_ENABLED = False
class Settings:
    """??????? ???? ????? ?????"""

    APP_NAME = "Phoenix Genesis"
    VERSION = "0.1.0"

    DEBUG = True

    DATA_PATH = "data"
    LOG_PATH = "logs"
    BACKUP_PATH = "backup"

    DEFAULT_EXCHANGE = "XT"

    DEMO_MODE = True
    REAL_EXECUTION_ENABLED = False

    # ─── Fee config (XT) ───
    FEE_MARKET = "futures"            # "spot" یا "futures"
    FEE_ORDER_TYPE = "taker"          # "maker" یا "taker"
    FEE_SPOT    = {"maker": 0.0020, "taker": 0.0020}   # 0.20% / 0.20%
    FEE_FUTURES = {"maker": 0.0002, "taker": 0.0006}   # 0.02% / 0.06%

    # ─── TP / SL ───
    AUTO_TP_SL = True
    TP_PCT = 0.0020    # 0.20%  → حد سود
    SL_PCT = 0.0010    # 0.10%  → حد ضرر
    MAX_POSITION_HOURS = 4

    # ─── Trend filter (EMA) ───
    TREND_FILTER_ENABLED = True
    EMA_FAST = 50
    EMA_SLOW = 200
    EMA_TIMEFRAME = "15m"
    EMA_LOOKBACK = 250
    # ─── Leverage ───
    LEVERAGE = 1                    # 1 = بدون اهرم، 3/5/10 = اهرم واقعی
    # ─── Trailing / BE / Partial TP ───
    PARTIAL_TP_ENABLED = True
    PARTIAL_TP_FRACTION = 0.5        # 50% در 1R
    PARTIAL_TP_AT_R = 1.0            # در 1R
    BE_ENABLED = True                # Break-even در 1R
    TRAILING_ENABLED = True
    TRAILING_START_R = 2.0           # شروع trail در 2R
    TRAILING_DISTANCE_R = 0.5        # فاصله 0.5R از best price