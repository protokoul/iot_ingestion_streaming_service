from typing import Literal

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing import Annotated

UserId = Annotated[str, StringConstraints(min_length=1, max_length=64, strip_whitespace=True)]
PersonName = Annotated[str, StringConstraints(min_length=1, max_length=128, strip_whitespace=True)]


class ManagedUserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UserId
    name: PersonName
    status: Literal["active", "inactive"]


class ManagedUserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: PersonName
    status: Literal["active", "inactive"]


class ManagedUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    name: str
    status: Literal["active", "inactive"]
