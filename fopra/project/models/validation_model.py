from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator

class Task(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: Optional[str] = Field(None, description="A description of the task.")
    startTime: Optional[str] = Field(None, description="The start time of the task in ISO 8601 format.")
    endTime: Optional[str] = Field(None, description="The end time of the task in ISO 8601 format.")
    location: Optional[str] = Field(None, description="The location associated with the task.")

    @validator("startTime", "endTime", pre=True, always=True)
    def validate_datetime(cls, value):
        """Ensure startTime and endTime are valid ISO 8601 datetime strings if provided."""
        if value is None:
            return value
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 datetime format: {value}")

class Observation(BaseModel):
    challenges: Optional[List[str]] = Field(default_factory=list, description="Challenges encountered during the operation.")
    successes: Optional[List[str]] = Field(default_factory=list, description="Successes achieved during the operation.")

class ExternalSupport(BaseModel):
    agencies: List[str] = Field(default_factory=list, description="Agencies providing external support.")

class OperationDetails(BaseModel):
    operationID: str = Field(..., description="A unique identifier for the operation.")
    operationName: str = Field(..., description="The name of the operation.")
    disasterType: str = Field(..., description="The type of disaster (e.g., flood, wildfire).")
    dateTime: str = Field(..., description="The date and time the operation began in ISO 8601 format.")
    duration: Optional[Union[int, float]] = Field(None, description="The duration of the operation in hours.")
    location: str = Field(..., description="The location where the operation is conducted.")

    @validator("dateTime", pre=True, always=True)
    def validate_datetime_format(cls, value):
        """Ensure dateTime is a valid ISO 8601 datetime string."""
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 datetime format: {value}")

class Report(BaseModel):
    operationDetails: OperationDetails
    resources: List[str] = Field(default_factory=list, description="Resources such as vehicles or equipment used in the operation.")
    tasks: List[Task] = Field(default_factory=list, description="Tasks carried out during the operation.")
    observations: Optional[Observation] = Field(None, description="Observations made during the operation.")
    externalSupport: Optional[ExternalSupport] = Field(None, description="External support received during the operation.")
