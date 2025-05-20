"""Utility functions and variables."""

from json import load
from os import environ
from dotenv import load_dotenv


load_dotenv()

FILEPATH: str = environ["FILEPATH"] or ""

valid_fields: list[str] = ["height", "weight", "bmi"]


def load_data() -> dict[str, dict[str, str | int | float]]:
    data: dict[str, dict[str, str | int | float]] = {}

    with open(FILEPATH, "r") as f:
        data = load(f)

    return data
