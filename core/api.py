from flask import Blueprint, request, make_response, jsonify
from db.schemas import habit_schema, HabitSchema, ToDoSchema, UserSchema
from db.database import db, Habit, ToDo, User
import datetime as dt
import itertools
from sqlalchemy import func, and_
from flask_restx import Api, Resource


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
        habits = Habit.query.filter(Habit.user_id == user_id).all()
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
        updates = HabitSchema(partial=True).load(body)
        Habit.query.filter(Habit.id == habit_id).update(updates)
        db.session.commit()
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

        subquery = (
            db.session.query(
                ToDo.habit_id, func.max(ToDo.current_scheduled_date).label("max_date")
            )
            .filter(
                ToDo.user_id == user_id,
                ToDo.type == "habit",
                ToDo.current_scheduled_date <= today,
                ToDo.done_date == None,
            )
            .group_by(ToDo.habit_id)
            .subquery()
        )

        # Main query to join the subquery and retrieve the latest scheduled habits
        latest_scheduled_habits = (
            db.session.query(ToDo)
            .join(
                subquery,
                and_(
                    ToDo.habit_id == subquery.c.habit_id,
                    ToDo.current_scheduled_date == subquery.c.max_date,
                ),
            )
            .all()
        )

        for habit in latest_scheduled_habits:
            if habit.done_date is None:
                habit.current_scheduled_date = today
                db.session.commit()

        ToDo.query.filter(
            ToDo.type == "task",
            ToDo.current_scheduled_date < today,
            ToDo.done_date is None,
            ToDo.user_id == user_id,
        ).update({"current_scheduled_date": today})
        db.session.commit()

        current_todos = ToDo.query.filter(
            ToDo.current_scheduled_date >= today,
            ToDo.current_scheduled_date <= end_date,
            ToDo.user_id == user_id,
        ).all()

        schedule_dicts = ToDoSchema(many=True, unknown="exclude").dump(current_todos)
        schedule_dicts = list(
            sorted(schedule_dicts, key=lambda x: x["currentScheduledDate"])
        )

        grouped_schedules = itertools.groupby(
            schedule_dicts, key=lambda x: x["currentScheduledDate"]
        )
        result = {}
        cur_date = dt.date.today()
        for date, _todos in grouped_schedules:
            while str(cur_date) != date:
                result[str(cur_date)] = []
                cur_date += dt.timedelta(days=1)

            if str(cur_date) == date:
                result[date] = list(_todos)
                cur_date += dt.timedelta(days=1)

        if not result.get(str(end_date)):
            result[str(end_date)] = []

        return jsonify(result) if result else jsonify({str(today): []})


@api.route("/users/<int:user_id>/todos/<int:todo_id>")
class todo(Resource):
    def patch(self, user_id, todo_id):
        body = request.get_json()
        updates = ToDoSchema(partial=True).load(body)
        ToDo.query.filter(ToDo.id == todo_id).update(updates)
        db.session.commit()
        return make_response("", 204)


@api.route("/delete")
class deleteall(Resource):
    def delete(self):
        db.session.query(Habit).delete()
        db.session.query(ToDo).delete()

        db.session.commit()
        return make_response("", 201)
