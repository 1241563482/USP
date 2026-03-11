"""Input parsing utilities."""

import csv
import json
from typing import List, Dict


def read_csv(path: str) -> List[Dict]:
    """Read a CSV file and return a list of records (dicts)."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def read_json(path: str) -> List[Dict]:
    """Read a JSON file containing a list of records."""
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON input must be a list of records")
    return data
