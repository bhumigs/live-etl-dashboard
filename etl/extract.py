import pandas as pd
import requests
from io import StringIO


def extract_data(source):
    """Extract data from CSV, JSON, or API URL"""
    if source.lower().endswith(".csv"):
        return pd.read_csv(source)
    elif source.lower().endswith(".json"):
        return pd.read_json(source)
    elif source.startswith("http"):
        response = requests.get(source)
        response.raise_for_status()
        return pd.read_json(StringIO(response.text))
    else:
        raise ValueError("Unsupported data source")
