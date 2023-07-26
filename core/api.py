import datetime as dt

from flask import Blueprint, jsonify, make_response, request
from flask_restx import Api, Resource

from db.database import Habit, ToDo, User, db
from db.schemas import HabitSchema, ToDoSchema, UserSchema, dump_todos, habit_schema
from utils import db_utils
from utils.scheduler import Scheduler

blueprint = Blueprint("app", __name__)
api = Api(blueprint)


@api.route("/users")
class users(Resource):
    def get(self):
        users = User.query.all()
        return UserSchema(many=True).dumps(users)

    def post(self):
        body = request.get_json()
        data = UserSchema().load(body)
        user = User(**data)

        db.session.add(user)
        db.session.commit()
        return UserSchema().dumps(user)

    def delete(self):
        db.session.query(User).delete()
        db.session.commit()
        return make_response("", 201)


@api.route("/users/<int:user_id>")
class user(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        return UserSchema().dumps(user) if user else make_response("", 404)

    def patch(self, user_id):
        body = request.get_json()
        updates = UserSchema(partial=True).load(body)
        User.query.filter(User.id == user_id).update(updates)
        db.session.commit()
        return make_response("", 204)

    def delete(self, user_id):
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return make_response("", 201)


@api.route("/users/<int:user_id>/habits")
class habits(Resource):
    def get(self, user_id):
        completion_rate_window = int(request.values.get("completion-rate-window", 0))

        habits = Habit.query.filter(Habit.user_id == user_id).all()
        if completion_rate_window != 0:
            for habit in habits:
                habit.completion_rate = db_utils.get_completion_rate(
                    habit.id,
                    dt.date.today() - dt.timedelta(days=completion_rate_window),
                    dt.date.today(),
                )
        return HabitSchema(many=True).dumps(habits)

    def delete(self, user_id):
        return "DELETE"

    def post(self, user_id):
        body = request.get_json()
        data = habit_schema.load(body)
        habit = Habit(**data, user_id=user_id)
        db.session.add(habit)
        db.session.commit()
        habit.schedule()
        return habit_schema.dumps(habit)


@api.route("/users/<int:user_id>/habits/<int:habit_id>")
class habit(Resource):
    def get(self, user_id, habit_id):
        habit = Habit.query.get(habit_id)
        return HabitSchema().dumps(habit)

    def delete(self, user_id, habit_id):
        habit = Habit.query.get(habit_id)
        db.session.delete(habit)
        db.session.commit()
        return make_response("", 201)

    def patch(self, user_id, habit_id):
        body = request.get_json()
        updates = HabitSchema(
            partial=True,
            only=[
                "name",
                "end_date",
                "completion_rate_target",
                "interval_type",
                "interval_value",
            ],
        ).load(body)
        Habit.query.filter(Habit.id == habit_id).update(updates)
        db.session.commit()
        if updates.get("interval_value"):
            Habit.query.get(habit_id).reschedule(from_date=dt.date.today())
        # elif updates.get("name"):
        #     ToDo.query.filter(ToDo.habit_id == habit_id).update(
        #         {"name": updates.get("name")}
        #     )
        #     db.session.commit()
        ToDo.query.filter(ToDo.habit_id == habit_id).update(**updates)
        db.session.commit()
        # TODO make patch available for all safe attrs
        return make_response("", 204)


@api.route("/users/<int:user_id>/todos")
class todos(Resource):
    def post(self, user_id):
        body = request.get_json()
        data = ToDoSchema().load(body)
        task = ToDo(**data, user_id=user_id)
        db.session.add(task)
        db.session.commit()

    def get(self, user_id):
        horizon = int(request.args.get("horizon", 0))
        today = request.args.get("today", str(dt.date.today()))
        today = dt.datetime.strptime(today, "%Y-%m-%d").date()
        end_date = today + dt.timedelta(days=horizon)

        sched = Scheduler(user_id, db, end_date)
        sched.reschedule()  # TODO only reschedule if it needs to be rescheduled...
        current_todos = sched.get_todos()

        result = dump_todos(current_todos, end_date)

        return jsonify(result)


@api.route("/users/<int:user_id>/todos/<int:todo_id>")
class todo(Resource):
    def patch(self, user_id, todo_id):
        body = request.get_json()
        updates = ToDoSchema(partial=True).load(body)
        ToDo.query.filter(ToDo.id == todo_id, ToDo.user_id == user_id).update(updates)
        db.session.commit()
        return make_response("", 204)


@api.route("/delete")
class deleteall(Resource):
    def delete(self):
        db.session.query(Habit).delete()
        db.session.query(ToDo).delete()

        db.session.commit()
        return make_response("", 201)
