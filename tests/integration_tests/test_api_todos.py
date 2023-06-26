from tests.conftest import (
    load_response,
    v1_url,
    habits_url,
    todos_url,
    users_url,
    keys_match,
    make_habit_dicts,
)
from datetime import date, timedelta
from db.database import Habit

today = str(date.today())
tmrw = str(date.today() + timedelta(days=1))
yday = str(date.today() - timedelta(days=1))


def test_e2e(client, new_user_with_habits, _app):
    """
    Tests end to end journey of the /todos endpoint.
    **
    """
    # assert GET habits works as expected
    user_id = new_user_with_habits()
    user_habits_url = habits_url.replace("<user_id>", str(user_id))
    response = client.get(user_habits_url)
    assert response.status_code == 200
    habits = load_response(response)
    assert len(habits) > 0

    # schedule the habits (as it's not done in pytest fixture)
    first_habit_id = habits[0]["id"]
    with _app.app_context():
        for habit in habits:
            Habit.query.get(habit["id"]).schedule()

    # assert all habits are scheduled correctly by GET to todos

    user_todos_url = todos_url.replace("<user_id>", str(user_id))
    response = client.get(user_todos_url)
    assert response.status_code == 200
    response = response.get_json()
    # all habits should be scheduled for today as they
    # weren't done on their start date (yday)
    assert len(response[today]) == len(habits)

    # update done and current schedule date to yday
    # this makes one less habit scheduled for today
    response = client.patch(
        f"{user_todos_url}/{first_habit_id}",
        json={"currentScheduledDate": yday, "doneDate": yday},
    )
    assert response.status_code == 204
    response = client.get(user_todos_url)
    assert response.status_code == 200
    response = response.get_json()
    assert len(response[today]) == len(habits) - 1
    assert len(response) == 1

    # check that increasing the horizon increases the number
    # of results returned
    response = client.get(f"{user_todos_url}?horizon=3")
    response = response.get_json()
    assert len(response) == 4


def test_weekly_habit(client, new_user):
    uid = new_user()
    user_habits_url = habits_url.replace("<user_id>", str(uid))
    user_todos_url = todos_url.replace("<user_id>", str(uid))
    habit_data = {
        "intervalType": "week",
        "intervalValue": 1,
        "name": "water plants",
    }
    response = client.post(user_habits_url, json=habit_data)
    assert response.status_code == 200

    response = client.get(user_todos_url)
    assert response.status_code == 200
    loaded = response.get_json()

def test_post_task(client, new_user):
    uid = new_user()
    user_todos_url = todos_url.replace("<user_id>", str(uid))
    task_data = {
        "name": "write to do list",
        "originalScheduledDate": today,
        "currentScheduledDate": today,
        "type": "task"
    }
    response = client.post(user_todos_url, json=task_data)
    assert response.status_code == 200

    response = client.get(user_todos_url)
    assert response.status_code == 200
    loaded = response.get_json()
    assert len(loaded[today]) == 1
