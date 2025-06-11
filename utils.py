"""Utility functions and variables"""

from json import load
from os import environ
from dotenv import load_dotenv

from db import collection


load_dotenv()

# Variables
FILEPATH: str = environ.get("FILEPATH", "")
sort_fields: list[str] = ["height", "weight", "bmi"]


# Functions
def load_data() -> dict[str, dict[str, str | int | float]]:
    """For loading the JSON data."""
    data: dict[str, dict[str, str | int | float]] = {}

    with open(FILEPATH, "r") as f:
        data = load(f)

    return data


def new_pid() -> str | None:
    """For generating new patient ID."""
    if collection is None:
        return None

    last_pid = collection.find_one(sort=[("pid", -1)])
    return f"P{int(last_pid['pid'][-1]) + 1:03}" if last_pid is not None else "P001"
