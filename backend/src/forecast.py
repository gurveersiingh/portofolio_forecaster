from __future__ import annotations

import pandas as pd
from prophet import Prophet

from .config import PROPHET_PARAMS


def forecast_next_price(price_series: pd.Series) -> float:
    """Fit Prophet on `price_series` and forecast the following calendar day."""
    history = pd.DataFrame({"ds": pd.to_datetime(price_series.index), "y": price_series.values})

    model = Prophet(**PROPHET_PARAMS)
    model.fit(history)

    next_day = history["ds"].max() + pd.Timedelta(days=1)
    forecast = model.predict(pd.DataFrame({"ds": [next_day]}))
    return float(forecast["yhat"].iloc[0])


def forecast_universe(price_data: dict[str, pd.DataFrame]) -> dict[str, dict[str, float]]:
    """Forecast every ticker and derive the implied one-day return.

    Returns e.g.
    {"AAPL": {"current_price": 190.1, "predicted_price": 191.4, "predicted_return": 0.0068}}
    """
    results: dict[str, dict[str, float]] = {}
    for ticker, df in price_data.items():
        current_price = float(df["price"].iloc[-1])
        predicted_price = forecast_next_price(df["price"])
        results[ticker] = {
            "current_price": current_price,
            "predicted_price": predicted_price,
            "predicted_return": (predicted_price - current_price) / current_price,
        }
    return results
