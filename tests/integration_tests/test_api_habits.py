from tests.conftest import (
    load_response,
    v1_url,
    habits_url,
    todos_url,
    users_url,
    keys_match,
)
from datetime import date, timedelta

today = str(date.today())
tmrw = str(date.today() + timedelta(days=1))
yday = str(date.today() - timedelta(days=1))


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
    # /habits
    ## post new habit
    post_body = {"name": "make ippo ippo", "intervalType": "day", "intervalValue": 2}
    post_response = client.post(user_habits_url, json=post_body)
    assert post_response.status_code == 200
    post_response_dict = load_response(post_response)
    assert post_response_dict["name"] == post_body["name"]
    assert keys_match(
        post_response_dict.keys(),
        expected_habit_keys,
    )

    ## get all habits
    get_response = client.get(user_habits_url)
    assert get_response.status_code == 200
    get_response_arr = load_response(get_response)
    assert isinstance(get_response_arr, list)
    assert len(get_response_arr) == 1
    assert get_response_arr[0] == post_response_dict

    habit_id = post_response_dict["id"]
    user_habit_url = f"{user_habits_url}/{habit_id}"
    # /habits/<habit_id>

    ## get habit
    get_response_single = client.get(user_habit_url)
    assert get_response_single.status_code == 200
    get_response_dict = load_response(get_response_single)
    assert keys_match(
        get_response_dict.keys(),
        expected_habit_keys,
    )

    ## patch habit
    patch_response = client.patch(user_habit_url, json={"intervalValue": 4})
    assert patch_response.status_code == 204
    get_response_single_patch = client.get(user_habit_url)
    assert get_response_single_patch.status_code == 200
    get_response_patch_dict = load_response(get_response_single_patch)
    assert get_response_patch_dict["intervalValue"] == 4
