from __future__ import annotations

import logging
import os
import uuid
from datetime import date, datetime, timezone

from supabase import Client, create_client

from .config import SUPABASE_TABLE

logger = logging.getLogger(__name__)


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set - see backend/.env.example"
        )
    return create_client(url, key)


def save_run(
    as_of: date,
    forecasts: dict[str, dict[str, float]],
    weights: dict[str, float],
) -> None:
    client = get_client()
    rows = [
        {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "as_of_date": as_of.isoformat(),
            "ticker": ticker,
            "current_price": data["current_price"],
            "predicted_price": data["predicted_price"],
            "predicted_return": data["predicted_return"],
            "weight": weights.get(ticker, 0.0),
        }
        for ticker, data in forecasts.items()
    ]
    client.table(SUPABASE_TABLE).insert(rows).execute()
    logger.info("Saved %d rows to Supabase table '%s'", len(rows), SUPABASE_TABLE)
