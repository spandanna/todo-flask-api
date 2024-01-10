import datetime as dt
import json
import random
import string
from typing import List

import pytest

from db.database import Habit, ToDo, User, db
from factory.build import create_app

v1_url = "/api/v1"
users_url = f"{v1_url}/users"
user_url = f"{users_url}/<user_id>"
habits_url = f"{user_url}/habits"
todos_url = f"{user_url}/todos"


@pytest.fixture
def app_fixture():
    app = create_app("config.TestConfig")
    return app


@pytest.fixture
def client(app_fixture):
    app = app_fixture
    yield app.test_client()
    with app.app_context():
        # lazy cleanup to make sure test data isn't left over
        db.session.query(Habit).delete()
        db.session.query(ToDo).delete()
        db.session.query(User).delete()
        db.session.commit()


def load_response(response):
    return json.loads(response.get_json())


def keys_match(actual_keys, expected_keys):
    return len(set(list(actual_keys)).intersection(expected_keys)) == len(expected_keys)


@pytest.fixture
def new_user(app_fixture):
    _uid = None

    def inner(name: str = None):
        with app_fixture.app_context():
            nonlocal _uid
            user = User(
                name=name
                or "".join(random.choice(string.ascii_letters) for i in range(10))
            )
            db.session.add(user)
            db.session.commit()
            _uid = user.id
        return _uid

    yield inner
    with app_fixture.app_context():
        _user = User.query.get(_uid)
        db.session.delete(_user)
        db.session.commit()


def make_habit_dicts(_uid, n: int = 3, contents: List[tuple] = None):
    if not contents:
        start_date = dt.date.today() - dt.timedelta(days=1)
        contents = [
            # TODO make random
            ("habit rabbit", "day", 3, _uid, start_date)
            for _ in range(n)
        ]
    return [
        {
            "name": t[0],
            "interval_type": t[1],
            "interval_value": t[2],
            "user_id": t[3],
            "start_date": t[4],
        }
        for t in contents
    ]


@pytest.fixture
def new_user_with_habits(app_fixture, new_user):
    """
    Fixture to populate the database with a new user and habits.
    Fixture can be used in a test to populate the user with inputted habits.
    Returns user ID.
    """
    _uid = None

    def inner(name: str = None, habit_dicts: list = None):
        nonlocal _uid
        _uid = new_user(name)
        with app_fixture.app_context():
            if not habit_dicts:
                habit_dicts = make_habit_dicts(_uid=_uid)
            else:
                habit_dicts = [dict(d, user_id=_uid) for d in habit_dicts]

            habits = [Habit(**habit_dict) for habit_dict in habit_dicts]
            db.session.bulk_save_objects(habits)
            db.session.commit()

            for habit in Habit.query.filter(Habit.user_id == _uid).all():
                habit.schedule()
        return _uid

    yield inner
