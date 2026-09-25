from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


FlightStatus = Literal["ON_TIME", "DELAYED", "CANCELLED"]


class Flight(BaseModel):
    flight_id: str
    airline: str
    origin: str
    destination: str

    scheduled_departure: datetime
    scheduled_arrival: datetime
    actual_arrival: datetime | None

    delay_minutes: int = Field(ge=0)
    status: FlightStatus


class Connection(BaseModel):
    connection_id: str
    passenger_id: str
    inbound_flight_id: str
    onward_flight_id: str

    minimum_connection_minutes: int = Field(
        ge=30,
        le=180,
    )


class AirportTransferTime(BaseModel):
    airport_code: str
    transfer_minutes: int = Field(
        ge=0,
        le=180,
    )