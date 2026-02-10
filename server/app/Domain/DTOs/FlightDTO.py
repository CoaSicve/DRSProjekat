from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FlightDTO(BaseModel):
    id: int
    name: str
    airline_id: int
    airline_name: str  # Dodatno za prikaz
    distance_km: float
    duration_minutes: int
    departure_time: datetime
    departure_airport: str
    arrival_airport: str
    created_by_user_id: int
    ticket_price: float
    status: str
    rejection_reason: Optional[str] = None

class CreateFlightDTO(BaseModel):
    name: str = Field(..., max_length=100)
    airline_id: int
    distance_km: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)
    departure_time: str  # Format: "YYYY-MM-DD HH:MM:SS"
    departure_airport: str = Field(..., max_length=100)
    arrival_airport: str = Field(..., max_length=100)
    ticket_price: float = Field(..., gt=0)