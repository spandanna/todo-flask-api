import datetime as dt

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from utils import utils

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=dt.datetime.utcnow)
    habits = db.relationship("Habit", back_populates="user", lazy=True)
    todos = db.relationship("ToDo", back_populates="user", lazy=True)


class Habit(db.Model):
    __tablename__ = "habits"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=dt.datetime.utcnow)
    start_date = db.Column(db.Date(), default=dt.date.today)
    end_date = db.Column(db.Date())
    # either
    interval_type = db.Column(db.String())  # e.g. day, week, month, year
    interval_value = db.Column(
        db.Integer()
    )  # frequency of the interval e.g. every 3 days
    # or
    day_of_week = db.Column(db.String())  # optional for day of week habits
    # could add day of month, week of year, month of year?
    # or
    repetition_type = db.Column(db.String())  # e.g. times per_week per_month
    repetition_value = db.Column(db.Integer())  # e.g. 3

    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="habits", lazy=True)
    scheduled = db.relationship("ToDo", back_populates="habit", lazy=True)

    def schedule(self, ahead_window=100):
        end_date = self.start_date + dt.timedelta(days=ahead_window)

        if self.interval_type == "day":
            interval_value_days = self.interval_value
        elif self.interval_type == "week":
            interval_value_days = self.interval_value * 7
        to_schedule_dates = utils.get_dates(
            self.start_date, interval_value_days, end_date
        )

        scheduled_habits = [
            ToDo(
                user_id=self.user_id,
                type="habit",
                habit_id=self.id,
                name=self.name,
                original_scheduled_date=date,
                scheduled_date=date,
                done_date=None,
            )
            for date in to_schedule_dates
        ]
        db.session.bulk_save_objects(scheduled_habits)
        db.session.commit()
        return

    def reschedule(self, from_date, ahead_window=100):
        end_date = from_date + dt.timedelta(days=ahead_window)

        if self.interval_type == "day":
            interval_value_days = self.interval_value
        elif self.interval_type == "week":
            interval_value_days = self.interval_value * 7

        # delete future schedule
        ToDo.query.filter(
            ToDo.habit_id == self.id, ToDo.scheduled_date >= from_date
        ).delete()

        to_schedule_dates = utils.get_dates(from_date, interval_value_days, end_date)

        scheduled_habits = [
            ToDo(
                user_id=self.user_id,
                type="habit",
                habit_id=self.id,
                name=self.name,
                original_scheduled_date=date,
                scheduled_date=date,
                done_date=None,
            )
            for date in to_schedule_dates
        ]
        db.session.bulk_save_objects(scheduled_habits)
        db.session.commit()
        return


def get_scheduled_date(context):
    """Gets the original scheduled date for a given ToDo"""
    return context.get_current_parameters()["scheduled_date"]


class ToDo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    type = db.Column(db.String)  # habit or task
    name = db.Column(db.String())
    original_scheduled_date = db.Column(
        db.Date(), default=get_scheduled_date
    )  # when it was originally scheduled for
    scheduled_date = db.Column(db.Date())  # current schedule date
    done_date = db.Column(db.Date())  # when it was done
    habit_id = db.Column(db.Integer(), db.ForeignKey("habits.id"))
    habit = db.relationship("Habit", back_populates="scheduled", lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="todos", lazy=True)
