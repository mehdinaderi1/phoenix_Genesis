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
    TP_PCT = 0.003    # 0.3%  → حد سود
    SL_PCT = 0.0015    # 0.15%  → حد ضرر
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
    BE_AT_R = 1.0                    # BE trigger R (decoupled from PARTIAL_TP_AT_R)
    TRAILING_ENABLED = True
    TRAILING_START_R = 1.5           # شروع trail در 1.5R
    TRAILING_DISTANCE_R = 0.3       # فاصله 0.3R از best price
    TP_EXTEND_AFTER_PARTIAL_R = 10   # بعد از partial، TP به 10R می‌رود
    # config/settings.py
    position_size_percent = 5.0     # یا 10.0