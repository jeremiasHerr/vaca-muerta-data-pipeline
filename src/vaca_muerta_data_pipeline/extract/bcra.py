"""Extract USD exchange rates from BCRA Estadisticas Cambiarias API"""

from datetime import date
from typing import Any

import requests

BCRA_BASE_URL = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0"
REQUEST_TIMEOUT_SECONDS = 30

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