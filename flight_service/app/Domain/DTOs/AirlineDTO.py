from pydantic import BaseModel, Field

class AirlineDTO(BaseModel):
    id: int
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    country: str = Field(..., max_length=50)

class CreateAirlineDTO(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    country: str = Field(..., max_length=50)