"""
Energy Consumption Forecast page: fetches the latest forecast artifacts
(Plotly figure, metadata and activity log) produced by the AutoML pipeline
from GCS.
"""

import logging

_GCS_BUCKET = "energy_consumption_automl"
_GCS_BLOB   = "forecast_plot.json"


def fetch_energy_forecast_data() -> dict | None:
    """Download the latest energy forecast Plotly JSON from GCS."""
    import json as _json
    from google.cloud import storage as _gcs

    try:
        client = _gcs.Client()
        blob = client.bucket(_GCS_BUCKET).blob(_GCS_BLOB)
        return _json.loads(blob.download_as_text(encoding="utf-8"))
    except Exception as exc:
        logging.warning(f"[EnergyForecast] Could not fetch forecast from GCS: {exc}")
        return None


def fetch_energy_forecast_metadata() -> dict | None:
    """Download the forecast metadata JSON from GCS."""
    import json as _json
    from google.cloud import storage as _gcs

    try:
        client = _gcs.Client()
        blob = client.bucket(_GCS_BUCKET).blob("forecast_metadata.json")
        return _json.loads(blob.download_as_text(encoding="utf-8"))
    except Exception as exc:
        logging.warning(f"[EnergyForecast] Could not fetch metadata from GCS: {exc}")
        return None


def fetch_energy_activity_log() -> list | None:
    """Download the pipeline activity log JSON from GCS (most recent last)."""
    import json as _json
    from google.cloud import storage as _gcs

    try:
        client = _gcs.Client()
        blob = client.bucket(_GCS_BUCKET).blob("activity_log.json")
        events = _json.loads(blob.download_as_text(encoding="utf-8"))
        return list(reversed(events))
    except Exception as exc:
        logging.warning(f"[EnergyForecast] Could not fetch activity log from GCS: {exc}")
        return None
