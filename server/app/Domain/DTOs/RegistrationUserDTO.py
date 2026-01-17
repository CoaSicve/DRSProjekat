from pydantic import BaseModel, Field

class RegistrationUserDTO(BaseModel):
    name: str = Field(..., max_length = 80)
    lastName: str = Field(..., max_length = 80)
    dateOfBirth: str = Field(None)
    email: str = Field(..., max_length = 120)
    role: str = Field(default = 'USER')
    password: str = Field(..., min_length = 6, max_length = 200)
    gender: str = Field(None, max_length = 20)
    state: str = Field(None, max_length = 50)
    street: str = Field(None, max_length = 100)
    number: str = Field(None, max_length = 20)
    accountBalance: float = Field(default = 0.0)
    