import datetime as dt

from tests.conftest import habits_url, keys_match, load_response, todos_url

today = str(dt.date.today())
tmrw = str(dt.date.today() + dt.timedelta(days=1))
yday = str(dt.date.today() - dt.timedelta(days=1))


def test_e2e(client, new_user):
    """
    Tests end to end journey of the /habits endpoint.
    /users/<user_id>/habits: POST, GET
    /users/<user_id>/habits/<user_id>: GET, PATCH, DELETE
    """
    expected_habit_keys = {
        "name",
        "id",
        "userId",
        "createdAt",
        "startDate",
        "endDate",
        "intervalType",
        "intervalValue",
    }

    user_id = new_user()
    user_habits_url = habits_url.replace("<user_id>", str(user_id))
    # post new habit
    post_body = {"name": "make ippo ippo", "intervalType": "day", "intervalValue": 2}
    post_response = client.post(user_habits_url, json=post_body)
    assert post_response.status_code == 200
    post_response_dict = load_response(post_response)
    assert post_response_dict["name"] == post_body["name"]
    assert keys_match(
        post_response_dict.keys(),
        expected_habit_keys,
    )

    # get all habits
    get_response = client.get(user_habits_url)
    assert get_response.status_code == 200
    get_response_arr = load_response(get_response)
    assert isinstance(get_response_arr, list)
    assert len(get_response_arr) == 1
    assert get_response_arr[0] == post_response_dict

    habit_id = post_response_dict["id"]
    user_habit_url = f"{user_habits_url}/{habit_id}"

    # get single habit
    get_response_single = client.get(user_habit_url)
    assert get_response_single.status_code == 200
    get_response_dict = load_response(get_response_single)
    assert keys_match(
        get_response_dict.keys(),
        expected_habit_keys,
    )

    # patch habit
    patch_response = client.patch(user_habit_url, json={"intervalValue": 4})
    assert patch_response.status_code == 204
    get_response_single_patch = client.get(user_habit_url)
    assert get_response_single_patch.status_code == 200
    get_response_patch_dict = load_response(get_response_single_patch)
    assert get_response_patch_dict["intervalValue"] == 4


def test_patch_habit_interval_value(client, new_user):
    """When the interval value is updated, the habit should be rescheduled."""
    user_id = new_user()
    habit = {
        "name": "habitty",
        "intervalType": "day",
        "intervalValue": 1,
        "startDate": today,
    }
    user_habits_url = habits_url.replace("<user_id>", str(user_id))
    post_response = client.post(user_habits_url, json=habit)

    user_todos_url = todos_url.replace("<user_id>", str(user_id))

    user_habit_url = f"{user_habits_url}/{load_response(post_response)['id']}"
    client.patch(user_habit_url, json={"intervalValue": 2})
    get_todos_response = client.get(user_todos_url + "?horizon=1")
    assert len(get_todos_response.get_json()[tmrw]) == 0
    assert len(get_todos_response.get_json()[today]) == 1


def test_patch_habit_name(client, new_user):
    """When the name is updated, the name should be update in todos too."""
    user_id = new_user()
    habit = {
        "name": "habitty",
        "intervalType": "day",
        "intervalValue": 1,
        "startDate": today,
    }
    user_habits_url = habits_url.replace("<user_id>", str(user_id))
    post_response = client.post(user_habits_url, json=habit)

    user_todos_url = todos_url.replace("<user_id>", str(user_id))
    new_name = "hobbity"
    user_habit_url = f"{user_habits_url}/{load_response(post_response)['id']}"
    client.patch(user_habit_url, json={"name": new_name})
    get_todos_response = client.get(user_todos_url + "?horizon=1")
    assert get_todos_response.get_json()[today][0]["name"] == new_name


def test_get_completion_rate(client, new_user_with_habits):
    uid = new_user_with_habits()
    response = client.get(
        f'{habits_url.replace("<user_id>", str(uid))}?completion-rate-window=7'
    )
    loaded = load_response(response)
    assert isinstance(loaded[0].get("completionRate"), float)
