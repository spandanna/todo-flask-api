from datetime import datetime, timedelta
from utils.scheduler import Scheduler

habits_data = [
    {
        "id": 1,
        "name": "Exercise",
        "createdAt": datetime.now(),
        "startDate": datetime.now().date(),
        "endDate": (datetime.now().date() + timedelta(days=30)),
        "intervalType": "day",
        "intervalValue": 1,
    },
    {
        "id": 2,
        "name": "Reading",
        "createdAt": datetime.now(),
        "startDate": datetime.now().date(),
        "endDate": (datetime.now().date() + timedelta(days=60)),
        "intervalType": "weekly",
        "intervalValue": 2,
    },
    {
        "id": 3,
        "name": "Meditation",
        "createdAt": datetime.now(),
        "startDate": datetime.now().date(),
        "endDate": (datetime.now().date() + timedelta(days=90)),
        "intervalType": "monthly",
        "intervalValue": 1,
    },
]


def test_init_():
    s = Scheduler()
    assert s.schedule == {}
    assert s.habits == []
    assert s.today
