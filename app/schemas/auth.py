from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated

Username = Annotated[str, StringConstraints(min_length=3, max_length=64, strip_whitespace=True)]
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class SignupRequest(BaseModel):
    username: Username
    password: Password


class LoginRequest(BaseModel):
    username: Username
    password: Password


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="bearer")
