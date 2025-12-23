from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserLoginDTO(BaseModel):
    user_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=1, max_length=50)

    model_config = ConfigDict(from_attributes=True)

    def get(self) -> tuple[str, str]:
        return self.email, self.password


class UserLoginResponseDTO(BaseModel):
    user_id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
