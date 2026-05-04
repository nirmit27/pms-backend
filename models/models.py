"""
Models - Data validation
"""

from os import environ
from dotenv import load_dotenv

from pytz import timezone as tz
from datetime import datetime, date

from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, computed_field, EmailStr

load_dotenv()
TIMEZONE: str = environ.get("TIMEZONE", "Asia/Kolkata")


class Patient(BaseModel):
    """Model for patient record data validation."""

    # Fields to be provided...
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="Name of the city of residence")]
    age: Annotated[
        int, Field(..., gt=0, lt=150, description="Age of the patient (in years)")
    ]
    gender: Annotated[
        Literal["male", "female", "others"],
        Field(..., description="Gender of the patient (male/female/other)"),
    ]
    height: Annotated[
        float, Field(..., gt=0, lt=25, description="Height of the patient (in meters)")
    ]
    weight: Annotated[
        float, Field(..., gt=0, description="Weight of the patient (in kilograms)")
    ]
    pid: Annotated[
        str, Field(..., min_length=4, max_length=4, description="Patient ID")
    ]
    date_of_discharge: Annotated[
        Optional[date], Field(None, description="Date discharge")
    ]

    # Optional field(s)
    email: Annotated[
        Optional[EmailStr], Field(None, description="Email ID of the patient")
    ]

    # Computed field(s)
    @computed_field
    @property
    def bmi(self) -> float:
        bmi: float = round(self.weight / (self.height**2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        verdict: str = ""

        if self.bmi < 16.0:
            verdict = "Severely Underweight"
        elif self.bmi < 17.0:
            verdict = "Moderately Underweight"
        elif self.bmi < 18.5:
            verdict = "Underweight"
        elif self.bmi < 25.0:
            verdict = "Normal Weight"
        elif self.bmi < 30.0:
            verdict = "Overweight"
        elif self.bmi < 35.0:
            verdict = "Moderately Obese"
        elif self.bmi < 40.0:
            verdict = "Severely Obese"
        else:
            verdict = "Very Severely Obese"

        return verdict

    @computed_field
    @property
    def date_of_admission(self) -> str:
        return str(datetime.now(tz=tz(TIMEZONE)).isoformat())


class PatientUpdate(BaseModel):
    """Model for patient record update validation."""

    name: Annotated[Optional[str], Field(None, description="Name of the patient")]
    city: Annotated[
        Optional[str], Field(None, description="Name of the city of residence")
    ]
    age: Annotated[
        Optional[int],
        Field(None, gt=0, lt=150, description="Age of the patient (in years)"),
    ]
    gender: Annotated[
        Optional[Literal["male", "female", "others"]],
        Field(None, description="Gender of the patient (male/female/other)"),
    ]
    height: Annotated[
        Optional[float],
        Field(None, gt=0, lt=25, description="Height of the patient (in meters)"),
    ]
    weight: Annotated[
        Optional[float],
        Field(None, gt=0, description="Weight of the patient (in kilograms)"),
    ]
    pid: Annotated[
        Optional[str], Field(None, min_length=4, max_length=4, description="Patient ID")
    ]
    date_of_admission: Annotated[
        Optional[date], Field(None, description="Date of admission")
    ]
    date_of_discharge: Annotated[
        Optional[date], Field(None, description="Date discharge")
    ]
    email: Annotated[
        Optional[EmailStr], Field(None, description="Email ID of the patient")
    ]

    @computed_field
    @property
    def bmi(self) -> Optional[float]:
        if self.height and self.weight:
            return round(self.weight / (self.height**2), 2)
        return None

    # Computed field(s)
    @computed_field
    @property
    def verdict(self) -> str:
        verdict: str = ""
        if self.bmi is None:
            return "NA"

        if self.bmi < 16.0:
            verdict = "Severely Underweight"
        elif self.bmi < 17.0:
            verdict = "Moderately Underweight"
        elif self.bmi < 18.5:
            verdict = "Underweight"
        elif self.bmi < 25.0:
            verdict = "Normal Weight"
        elif self.bmi < 30.0:
            verdict = "Overweight"
        elif self.bmi < 35.0:
            verdict = "Moderately Obese"
        elif self.bmi < 40.0:
            verdict = "Severely Obese"
        else:
            verdict = "Very Severely Obese"

        return verdict


class Activity(BaseModel):
    """Model for activity log entries."""

    action_type: Annotated[
        Literal[
            "patient_admitted", "patient_updated", "patient_discharged", "system_check"
        ],
        Field(..., description="Type of action performed by user"),
    ]
    patient_id: Annotated[
        Optional[str], Field(None, description="Patient ID (if applicable)")
    ]
    patient_name: Annotated[
        Optional[str], Field(None, description="Patient name (if applicable)")
    ]
    description: Annotated[
        str, Field(..., description="Human-readable description of the activity")
    ]
    timestamp: Annotated[
        Optional[str], Field(None, description="When the activity occurred")
    ] = None

    def __init__(self, **data):
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = str(datetime.now(tz=tz(TIMEZONE)).isoformat())
        super().__init__(**data)
