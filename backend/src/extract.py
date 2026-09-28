from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_price_history(ticker: str, start: str, end: str) -> pd.DataFrame | None:
    """Return a DataFrame with `price` and `return` columns, indexed by date."""
    try:
        raw = yf.Ticker(ticker).history(start=start, end=end)
    except Exception:
        logger.exception("Could not download %s", ticker)
        return None

    if raw.empty:
        logger.warning("No data returned for %s", ticker)
        return None

    df = raw[["Close"]].rename(columns={"Close": "price"})
    df["return"] = df["price"].pct_change()
    df = df.dropna()
    df.index = pd.to_datetime(df.index).date
    df.index.name = "date"
    return df


def fetch_universe(tickers: list[str], start: str, end: str) -> dict[str, pd.DataFrame]:
    """Download history for every ticker, silently skipping any that fail."""
    data: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        history = fetch_price_history(ticker, start, end)
        if history is not None:
            data[ticker] = history
    return data


def align_on_common_dates(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Trim every DataFrame down to the dates that exist for *all* tickers."""
    if not data:
        return {}
    common = sorted(set.intersection(*(set(df.index) for df in data.values())))
    return {ticker: df.loc[common] for ticker, df in data.items()}
