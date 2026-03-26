import time

import pytest
from pydantic import ValidationError

from app.schemas.iot import IoTDataIn


def test_iot_schema_accepts_valid_payload() -> None:
    payload = IoTDataIn(
        user_id="U1001",
        metric_1=50.0,
        metric_2=100.0,
        metric_3=1,
        timestamp=int(time.time()),
    )
    assert payload.user_id == "U1001"


def test_iot_schema_rejects_future_timestamp() -> None:
    with pytest.raises(ValidationError):
        IoTDataIn(
            user_id="U1001",
            metric_1=50.0,
            metric_2=100.0,
            metric_3=1,
            timestamp=int(time.time()) + 600,
        )


def test_iot_schema_rejects_metric_out_of_range() -> None:
    with pytest.raises(ValidationError):
        IoTDataIn(
            user_id="U1001",
            metric_1=150.0,
            metric_2=100.0,
            metric_3=1,
            timestamp=int(time.time()),
        )
