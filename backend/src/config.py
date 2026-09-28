from __future__ import annotations

import os
from datetime import datetime, timezone

TICKERS: list[str] = [
    t.strip() for t in os.environ.get("TICKERS", "AAPL,MSFT,GOOGL,AMZN,NVDA").split(",") if t.strip()
]

START_DATE: str = os.environ.get("START_DATE", "2023-01-01")
END_DATE: str = os.environ.get("END_DATE", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

RISK_AVERSION: float = float(os.environ.get("RISK_AVERSION", "5"))
MIN_WEIGHT: float = float(os.environ.get("MIN_WEIGHT", "0.0"))
MAX_WEIGHT: float = float(os.environ.get("MAX_WEIGHT", "1.0"))
LOOKBACK_DAYS: int = int(os.environ.get("LOOKBACK_DAYS", "252"))

PROPHET_PARAMS = {
    "yearly_seasonality": True,
    "weekly_seasonality": True,
    "daily_seasonality": False,
}

SUPABASE_TABLE: str = os.environ.get("SUPABASE_TABLE", "predictions")
