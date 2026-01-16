from pydentic import BaseModel, Field

class UserDTO(BaseModel):
    id: int = Field(...)
    name: str = Field(..., max_length = 80)
    lastName: str = Field(..., max_length = 80)
    email: str = Field(..., max_length = 120)
    role: enumerate = Field(..., default = 'USER')
    profileImage: str = Field(None, max_length = 200)