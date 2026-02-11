from pydantic import BaseModel, Field
from typing import Optional

class UserDTO(BaseModel):
    id: int
    name: str = Field(..., max_length = 80)
    lastName: str = Field(..., max_length = 80)
    gender: str = Field(None, max_length = 20)
    dateOfBirth: str = Field(None)
    email: str = Field(..., max_length = 120)
    role: str = Field(default = 'USER')
    profileImage: Optional[str] = Field(None, max_length = 200)
    state: str = Field(None, max_length = 50)
    street: str = Field(None, max_length = 100)
    number: str = Field(None, max_length = 20)
    accountBalance: float = Field(default = 0.0)