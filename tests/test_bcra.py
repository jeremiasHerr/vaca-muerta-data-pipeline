"""Tests for the BCRA extraction module."""

from datetime import date

import pandas as pd
import pytest

from vaca_muerta_data_pipeline.extract.bcra import (
    OUTPUT_COLUMNS,
    fetch_usd_rates,
    parse_usd_rates,
)

SAMPLE_PAYLOAD = {
    "status": 200,
    "metadata": {"resultset": {"count": 2, "offset": 0, "limit": 1000}},
    "results": [
        {
            "fecha": "2026-11-13",
            "detalle": [
                {
                    "codigoMoneda": "USD",
                    "descripcion": "DOLAR E.E.U.U.",
                    "tipoPase": 0.0,
                    "tipoCotizacion": 1543.5,
                }
            ],
        },
        {
            "fecha": "2026-11-12",
            "detalle": [
                {
                    "codigoMoneda": "USD",
                    "descripcion": "DOLAR E.E.U.U.",
                    "tipoPase": 0.0,
                    "tipoCotizacion": 1545.5,
                }
            ],
        },
    ],
}

EMPTY_PAYLOAD = {
    "status": 200,
    "metadata": {"resultset": {"count": 0, "offset": 0, "limit": 1000}},
    "results": [],
}

def test_parse_returns_one_row_per_date_sorted_ascending():
    df = parse_usd_rates(SAMPLE_PAYLOAD)

    assert list(df.columns) == OUTPUT_COLUMNS
    assert len(df) == 2
    assert df["date"].is_monotonic_increasing #checks if the order is ascending
    assert df.loc[0, "rate"] == 1545.5


def test_parse_converts_date_column_to_datetime():
    df = parse_usd_rates(SAMPLE_PAYLOAD)

    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_parse_empty_results_returns_empty_dataframe_with_columns():
    df = parse_usd_rates(EMPTY_PAYLOAD)

    assert df.empty
    assert list(df.columns) == OUTPUT_COLUMNS


def test_fetch_rejects_start_after_end():
    with pytest.raises(ValueError):
        fetch_usd_rates(date(2026, 11, 20), date(2026, 11, 10))