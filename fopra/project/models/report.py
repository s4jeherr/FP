from dataclasses import dataclass
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

@dataclass
class Report:
    """Data model for fire department reports"""
    einsatzart: str
    ort: str
    datum: datetime
    dauer: str
    beteiligte: List[str]
    verlauf: str

    def to_dict(self):
        """Convert report to dictionary format"""
        return {
            'einsatzart': self.einsatzart,
            'ort': self.ort,
            'datum': self.datum.strftime('%Y-%m-%d'),
            'dauer': self.dauer,
            'beteiligte': self.beteiligte,
            'verlauf': self.verlauf
        }

    @classmethod
    def create(cls, **kwargs):
        """Create report with default values for missing fields"""
        default_value = "K.A."
        defaults = {
            'einsatzart': default_value,
            'ort': default_value,
            'datum': datetime.now(),
            'dauer': default_value,
            'beteiligte': [default_value],
            'verlauf': default_value
        }
        defaults.update(kwargs)
        return cls(**defaults)

# Extended Report Models for validation
class Task(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: str = Field(None, description="A description of the task.")
    startTime: datetime = Field(None, description="The start time of the task.")
    endTime: datetime = Field(None, description="The end time of the task.")
    location: str = Field(..., description="The location associated with the task.")

class Observation(BaseModel):
    challenges: List[str] = Field(..., description="Challenges encountered during the operation.")
    successes: List[str] = Field(..., description="Successes achieved during the operation.")

class ExternalSupport(BaseModel):
    agencies: List[str] = Field(..., description="Agencies providing external support.")

class OperationDetails(BaseModel):
    operationID: str = Field(..., description="A unique identifier for the operation.")
    operationName: str = Field(..., description="The name of the operation.")
    disasterType: str = Field(..., description="The type of disaster (e.g., flood, wildfire).")
    dateTime: datetime = Field(..., description="The date and time the operation began.")
    duration: float = Field(None, description="The duration of the operation in hours.")
    location: str = Field(..., description="The location where the operation is conducted.")

class ExtendedReport(BaseModel):
    operationDetails: OperationDetails
    resources: List[str] = Field(..., description="Resources such as vehicles or equipment used in the operation.")
    tasks: List[Task] = Field(..., description="Tasks carried out during the operation.")
    observations: Observation
    externalSupport: ExternalSupport