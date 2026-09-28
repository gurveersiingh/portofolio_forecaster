from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import LOOKBACK_DAYS, MAX_WEIGHT, MIN_WEIGHT, RISK_AVERSION


def covariance_matrix(price_data: dict[str, pd.DataFrame], lookback_days: int = LOOKBACK_DAYS) -> pd.DataFrame:
    """Historical return covariance over the trailing `lookback_days`."""
    returns = pd.DataFrame({ticker: df["return"].tail(lookback_days) for ticker, df in price_data.items()})
    return returns.cov()


def optimise_weights(
    expected_returns: dict[str, float],
    price_data: dict[str, pd.DataFrame],
    risk_aversion: float = RISK_AVERSION,
    min_weight: float = MIN_WEIGHT,
    max_weight: float = MAX_WEIGHT,
) -> dict[str, float]:
    """Solve max(mu^T w - risk_aversion/2 * w^T Sigma w) s.t. sum(w) = 1, min<=w<=max.

    `mu` is the vector of Prophet-predicted one-day returns, and `Sigma` is the
    historical covariance matrix of daily returns.
    """
    tickers = list(expected_returns.keys())
    mu = np.array([expected_returns[t] for t in tickers])
    cov = covariance_matrix(price_data)[tickers].loc[tickers].to_numpy()

    def objective(w: np.ndarray) -> float:
        port_return = w @ mu
        port_variance = w @ cov @ w
        return -(port_return - 0.5 * risk_aversion * port_variance)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(min_weight, max_weight)] * len(tickers)
    x0 = np.full(len(tickers), 1 / len(tickers))

    result = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not result.success:
        raise RuntimeError(f"Optimisation did not converge: {result.message}")

    return dict(zip(tickers, result.x.tolist()))
