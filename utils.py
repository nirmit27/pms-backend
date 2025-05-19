"""Some utility functions and variables."""

from json import load
from os import environ
from dotenv import load_dotenv

load_dotenv()

# Environment vars.
FILEPATH: str = environ["FILEPATH"] or ""

valid_fields: list[str] = ["height", "weight", "bmi"]


def load_data() -> dict:
    data: dict = {}

    with open(FILEPATH, "r") as f:
        data = load(f)

    return data
