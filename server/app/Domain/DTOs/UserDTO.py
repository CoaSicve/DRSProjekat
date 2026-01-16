from pydantic import BaseModel, Field

class UserDTO(BaseModel):
    id: int
    name: str = Field(..., max_length = 80)
    lastName: str = Field(..., max_length = 80)
    email: str = Field(..., max_length = 120)
    role: str
    profileImage: str = Field(None, max_length = 200)