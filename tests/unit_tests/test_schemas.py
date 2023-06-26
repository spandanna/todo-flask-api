from db.schemas import habit_schema
import pytest
from marshmallow import ValidationError
from datetime import date, timedelta, datetime
import inflection
import uuid

today = date.today()
tmrw = date.today() + timedelta(1)
now = datetime.utcnow()
id = uuid.uuid4()


def test_habit_dumponly():
    actual = habit_schema.load({"id": id, "createdAt": now}, partial=True)
    assert len(actual) == 0
    actual = habit_schema.dump({"id": id, "created_at": now})
    assert actual["id"]
    assert actual["createdAt"]


def test_habit_load_name():
    with pytest.raises(ValidationError, match="name"):
        habit_schema.load({})


def test_habit_load_dates():
    payload = {"startDate": str(today), "endDate": str(tmrw)}
    actual = habit_schema.load(payload, partial=True)
    for key in payload.keys():
        assert actual[inflection.underscore(key)]
