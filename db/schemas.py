import datetime as dt
import itertools

from marshmallow import Schema, fields

from db.database import Habit, ToDo


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    created_at = fields.DateTime(data_key="createdAt", dump_only=True)


class HabitSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    user_id = fields.Integer(data_key="userId")
    created_at = fields.DateTime(data_key="createdAt", dump_only=True)
    start_date = fields.Date(data_key="startDate", dump_default=None)
    end_date = fields.Date(data_key="endDate", dump_default=None)

    interval_type = fields.String(data_key="intervalType")
    interval_value = fields.Integer(data_key="intervalValue")

    class Meta:
        ordered = True
        model = Habit


habit_schema = HabitSchema(unknown="exclude")


class ToDoSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    type = fields.String()
    name = fields.String()
    habit_id = fields.Integer(data_key="habitId", default=None)
    original_scheduled_date = fields.Date(data_key="originalScheduledDate")
    current_scheduled_date = fields.Date(data_key="currentScheduledDate")
    done_date = fields.Date(data_key="doneDate")

    class Meta:
        ordered = True
        model = ToDo


def dump_todos(todo_objects, end_date):
    todo_dicts = ToDoSchema(many=True, unknown="exclude").dump(todo_objects)
    todo_dicts = list(sorted(todo_dicts, key=lambda x: x["currentScheduledDate"]))

    daily_todo_dicts = itertools.groupby(
        todo_dicts, key=lambda x: x["currentScheduledDate"]
    )
    result = {}
    cur_date = dt.date.today()
    for date, _todos in daily_todo_dicts:
        while str(cur_date) != date:
            result[str(cur_date)] = []
            cur_date += dt.timedelta(days=1)

        if str(cur_date) == date:
            result[date] = list(_todos)
            cur_date += dt.timedelta(days=1)

    if not result.get(str(end_date)):
        result[str(end_date)] = []
    return result
