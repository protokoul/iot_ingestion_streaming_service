from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

Metric1 = Annotated[float, Field(ge=0, le=100)]
Metric2 = Annotated[float, Field(ge=0, le=200)]
Metric3 = Annotated[int, Field()]
Timestamp = Annotated[int, Field(description="Unix timestamp in seconds")]


class IoTDataIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    metric_1: Metric1
    metric_2: Metric2
    metric_3: Metric3
    timestamp: Timestamp

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_not_be_in_future(cls, value: int) -> int:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if value > now_ts:
            raise ValueError("timestamp must not be in the future")
        return value


class IoTDataOut(IoTDataIn):
    pass


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: str
    data: IoTDataOut
