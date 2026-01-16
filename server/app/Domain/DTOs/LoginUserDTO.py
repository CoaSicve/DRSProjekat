from pydantic import BaseModel, Field

class LoginUserDTO(BaseModel):
    email: str = Field(..., max_length = 120)
    password: str = Field(..., min_length = 6, max_length = 200)