import datetime as dt
import json

import requests


class ToDoApp:
    default_url = "http://127.0.0.1:8080"
    default_api_url = f"{default_url}/api/v1"
    default_users_url = f"{default_api_url}/users"

    def __init__(
        self,
        user_id: int = None,
        name: str = None,
        url: str = None,
        horizon: int = 7,
    ):
        if user_id:
            self.user_id = user_id
            self.name = None

        elif name:
            self.user_id = None
            self.name = name

        self.horizon = horizon
        self.url = url if url else self.default_url
        self.api_url = f"{self.url}/api/v1"
        self.users_url = f"{self.api_url}/users"

        self.user_url = f"{self.users_url}/{user_id}"
        self.user = None

        self.habits_url = f"{self.user_url}/habits"
        self._set_habits()

        self.todos_url = f"{self.user_url}/todos"
        self.todos = None
        self._set_todos()

        self._set_user()

    @classmethod
    def existing_from_id(cls, user_id: int):
        user = cls(user_id=user_id)
        user.name = user.user["name"]
        return user

    @classmethod
    def create_new_user(cls, user_name: str, url: str = None):
        response = requests.post(cls.default_users_url, json={"name": user_name})
        response.raise_for_status()
        response = json.loads(response.json())
        instance = cls(user_id=response["id"])
        instance.name = instance.user["name"]
        return instance

    def _get_user(self):
        response = requests.get(self.user_url)
        response.raise_for_status()
        return json.loads(response.json())

    def _set_user(self):
        self.user = self._get_user()
        return None

    def _get_habits(self):
        response = requests.get(self.habits_url)
        response.raise_for_status()
        return json.loads(response.json())

    def _set_habits(self):
        self.habits = self._get_habits()
        return None

    def _get_todos(self):
        response = requests.get(f"{self.todos_url}?horizon={self.horizon}")
        response.raise_for_status()
        return response.json()

    def _set_todos(self):
        self.todos = self._get_todos()
        return None

    def set_complete(self, todo_id: int = None, date: str = None, name: str = None):
        if todo_id:
            url = f"{self.todos_url}/{todo_id}"
        elif name and date:
            target_todos = self.todos.get(date)
            id = list(filter(lambda x: x["name"] == name, target_todos))[0]["id"]
            url = f"{self.todos_url}/{id}"
        if not date:
            date = str(dt.date.today())

        response = requests.patch(url, json={"doneDate": date})
        response.raise_for_status()
        self._set_todos()
        return None

    def new_task(self, name: str, do_date: str = None):
        if not do_date:
            do_date = str(dt.date.today())
        body = {"name": name, "scheduledDate": do_date, "type": "task"}
        response = requests.post(self.todos_url, json=body)
        response.raise_for_status()
        self._set_todos()
        return None

    def new_habit(
        self,
        name: str,
        interval_value: int,
        interval_type: str = "day",
        start_date: str = None,
    ):
        body = {
            "name": name,
            "intervalType": interval_type,
            "intervalValue": interval_value,
            "startDate": start_date,
        }
        response = requests.post(self.habits_url, json=body)
        response.raise_for_status()
        self._set_todos()
        self._set_habits()
        return None
