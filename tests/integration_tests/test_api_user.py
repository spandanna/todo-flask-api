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


def test_e2e(client):
    """
    Tests end to end journey of the /users endpoint.
    /users: POST, GET, # TODO DELETE
    /users/<user_id>: PATCH, GET, DELETE
    """
    # /users
    ## post new user
    post_body = {"name": "anna"}
    post_response = client.post(users_url, json=post_body)
    assert post_response.status_code == 200
    post_response_dict = load_response(post_response)
    assert keys_match(post_response_dict.keys(), {"name", "id", "createdAt"})

    # getting all users
    get_response = client.get(users_url)
    assert get_response.status_code == 200
    get_response_arr = load_response(get_response)
    assert isinstance(get_response_arr, list)

    uid = post_response_dict["id"]
    user_url = f"{users_url}/{uid}"
    ## /users/<user_id>
    # patch user data
    patch_body = {"name": "spanna"}
    patch_response = client.patch(user_url, json=patch_body)
    assert patch_response.status_code == 204

    # get single user and check patch update has been done
    get_response_single = client.get(user_url)
    assert get_response_single.status_code == 200
    get_response_single_dict = load_response(get_response_single)
    assert get_response_single_dict["name"] == patch_body["name"]

    # delete user and check db empty
    del_response = client.delete(user_url)
    assert del_response.status_code == 201

    get_response_del = client.get(user_url)
    assert get_response_del.status_code == 404


# def test_get_route(client):
#     resp = client.get(v1)
#     assert resp.status_code == 200
#     assert load_response(resp)["version"] == "0.1"


# def test_get_habits(client):
#     resp = client.get(habits)
#     assert resp.status_code == 200


# def test_post_habits(client):
#     post_payload = {
#         "name": "wani kani",
#         "intervalType": "day",
#         "intervalValue": 2,
#         "startDate": "2023-06-11",
#     }
#     resp = client.post(habits, json=post_payload)
#     assert resp.status_code == 200
#     assert list(load_response(resp).keys()) == [
#         "id",
#         "name",
#         "createdAt",
#         "startDate",
#         "endDate",
#         "intervalType",
#         "intervalValue",
#     ]


# def test_todo(client):
#     post_payload = {
#         "name": "wani kani",
#         "intervalType": "day",
#         "intervalValue": 2,
#         "startDate": today,
#     }
#     resp = client.post(habits, json=post_payload)
#     assert resp.status_code == 200
#     post_payload = {
#         "name": "stretching",
#         "intervalType": "day",
#         "intervalValue": 1,
#         "startDate": tmrw,
#     }
#     resp = client.post(habits, json=post_payload)
#     assert resp.status_code == 200
#     habit_id = load_response(resp).get("id")
#     resp = client.get(f"{todo}?horizon=1")
#     assert resp.status_code == 200
#     resp = load_response(resp)
#     assert len(resp.get(today)) == 1
#     assert len(resp.get(tmrw)) == 1
#     resp = client.patch(f"{todo}?habitId={habit_id}&date={tmrw}&isCompleted=true")
#     assert resp.status_code == 204


# def test_todo_overdue(client):
#     """
#     the todo is scheduled for yesterday but it wasn't done yesterday
#     the todo should be rescheduled for today
#     """
#     post_payload = {
#         "name": "wani kani",
#         "intervalType": "day",
#         "intervalValue": 2,
#         "startDate": str(date.today() - timedelta(days=3)),
#     }
#     resp = client.post(habits, json=post_payload)
#     habit_id_1 = load_response(resp).get("id")
#     post_payload = {
#         "name": "wani kani",
#         "intervalType": "day",
#         "intervalValue": 3,
#         "startDate": str(date.today() - timedelta(days=5)),
#     }
#     resp = client.post(habits, json=post_payload)
#     assert resp.status_code == 200
#     habit_id_2 = load_response(resp).get("id")

#     resp = client.get(f"{todo}?today={today}&horizon=0")
#     assert resp.status_code == 200
#     resp = load_response(resp)
#     assert len(resp.get(today)) == 2

#     resp = client.patch(
#         f"{todo}?habitId={habit_id_1}&date={str(date.today() - timedelta(days=2))}&isCompleted=true"
#     )

#     resp = client.get(f"{todo}?today={today}")
#     assert resp.status_code == 200
#     resp = load_response(resp)
#     assert len(resp.get(today)) == 1

#     # resp = client.patch(f"{todo}?habitId={habit_id}&date={today}&isCompleted=true")
#     # assert resp.status_code == 204


# def test_todo_overdue_2(client):
#     """
#     the todo is scheduled for yesterday but it wasn't done yesterday
#     the todo should be rescheduled for today
#     """
#     post_payload = {
#         "name": "wani kani less",
#         "intervalType": "day",
#         "intervalValue": 2,
#         "startDate": str(date.today() - timedelta(days=3)),
#     }
#     resp = client.post(habits, json=post_payload)
#     habit_id_1 = load_response(resp).get("id")
#     post_payload = {
#         "name": "wani kani",
#         "intervalType": "day",
#         "intervalValue": 3,
#         "startDate": str(date.today() - timedelta(days=5)),
#     }
#     resp = client.post(habits, json=post_payload)
#     assert resp.status_code == 200
#     habit_id_2 = load_response(resp).get("id")

#     resp = client.patch(
#         f"{todo}?habitId={habit_id_1}&date={str(date.today() - timedelta(days=1))}&isCompleted=true"
#     )

#     resp = client.get(f"{todo}?today={today}")
#     assert resp.status_code == 200
#     resp = load_response(resp)
#     assert len(resp.get(today)) == 1
