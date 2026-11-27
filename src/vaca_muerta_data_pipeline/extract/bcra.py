"""Extract USD exchange rates from BCRA Estadisticas Cambiarias API"""

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
import requests


BCRA_BASE_URL = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0"
REQUEST_TIMEOUT_SECONDS = 30
OUTPUT_COLUMNS = ["date", "currency", "rate"]


def fetch_usd_rates(start: date, end: date) -> dict[str, Any]:
    """Fetch USD exchange rates from the BCRA API for a date range.

    Both bounds are inclusive, matching the API behavior

    Args:
        start: First date of the range (inclusive)
        end: Last date of the range (inclusive)

    Returns:
        The raw JSON response as a dictionary

    Raises:
        ValueError: If start is after end
        requests.HTTPError: If the API returns an error status
    """
    if start > end:
        raise ValueError(f"start ({start}) must not be after end ({end})")
    url = f"{BCRA_BASE_URL}/Cotizaciones/USD"
    params = {"fechadesde": start.isoformat(), "fechahasta": end.isoformat()}
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def parse_usd_rates(payload: dict[str, Any]) -> pd.DataFrame:
    """Flatten the BCRA rates response into one row per date.

    Args:
        payload: Raw JSON returned by fetch_usd_rates.

    Returns:
        DataFrame with columns date, currency and rate, sorted by date.
        Empty (with the same columns) if the response has no results.
    """
    results = payload["results"]
    if not results:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    df = pd.json_normalize(results, record_path="detalle", meta=["fecha"])
    df = df.rename(
        columns={
            "fecha": "date",
            "codigoMoneda": "currency",
            "tipoCotizacion": "rate",
        }
    )[OUTPUT_COLUMNS]
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    return df.sort_values("date").reset_index(drop=True)

def extract_usd_rates(start: date, end: date) -> pd.DataFrame:
    """Fetch and parse USD rates, adding the extraction timestamp.

    Args:
        start: First date of the range (inclusive).
        end: Last date of the range (inclusive).

    Returns:
        Parsed rates with an extra extracted_at column in UTC.
    """
    df = parse_usd_rates(fetch_usd_rates(start, end))
    df["extracted_at"] = datetime.now(timezone.utc)
    return df    
