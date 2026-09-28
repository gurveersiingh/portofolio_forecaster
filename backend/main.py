from __future__ import annotations

import logging
from datetime import datetime

from src.config import END_DATE, START_DATE, TICKERS
from src.extract import align_on_common_dates, fetch_universe
from src.forecast import forecast_universe
from src.optimize import optimise_weights
from src.storage import save_run

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    logger.info("Fetching price history for %s", TICKERS)
    price_data = align_on_common_dates(fetch_universe(TICKERS, START_DATE, END_DATE))
    if not price_data:
        raise SystemExit("No price data downloaded - aborting.")

    logger.info("Forecasting next-day prices with Prophet (one model per ticker, this is the slow step)")
    forecasts = forecast_universe(price_data)

    logger.info("Solving for optimal mean-variance weights")
    expected_returns = {t: f["predicted_return"] for t, f in forecasts.items()}
    weights = optimise_weights(expected_returns, price_data)

    as_of = datetime.strptime(END_DATE, "%Y-%m-%d").date()
    save_run(as_of, forecasts, weights)

    for ticker, w in sorted(weights.items(), key=lambda kv: -kv[1]):
        logger.info(
            "%-6s weight %5.1f%%  predicted return %+.2f%%",
            ticker,
            w * 100,
            forecasts[ticker]["predicted_return"] * 100,
        )


if __name__ == "__main__":
    run()
