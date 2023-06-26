import datetime as dt

from sqlalchemy import and_, func

from db.database import Habit, ToDo


class Scheduler:
    def __init__(self, user_id, db, end_date, today=None):
        self.end_date = end_date
        self.user_id = user_id
        self.db = db
        self.todos = []
        self.habits = []
        self.today = dt.date.today()
        self.scheduling_types = {
            "intervalDay": ("intervalType", "day"),
            "intervalWeek": ("intervalType", "weekly"),
            # "intervalMonth": ("intervalType", "monthly"),
        }
        self.habits_by_scheduling_type = []

    def reschedule(self):
        self._reschedule_habits()
        self._reschedule_tasks()
        self.set_todos()

    def set_todos(self):
        self.todos = ToDo.query.filter(
            ToDo.current_scheduled_date >= self.today,
            ToDo.current_scheduled_date <= self.end_date,
            ToDo.user_id == self.user_id,
        ).all()

    def get_todos(self):
        return self.todos

    def _reschedule_tasks(self):
        ToDo.query.filter(
            ToDo.type == "task",
            ToDo.current_scheduled_date < self.today,
            ToDo.done_date is None,
            ToDo.user_id == self.user_id,
        ).update({"current_scheduled_date": self.today})
        self.db.session.commit()

    def _reschedule_habits(self):
        latest_habits = self._get_latest_scheduled_habits()
        for habit in latest_habits:
            if habit.done_date is None and habit.current_scheduled_date != self.today:
                habit.current_scheduled_date = self.today
                self.db.session.commit()

    def _get_latest_scheduled_habits(self):
        # Find the latest scheduled date up until today for each habit
        subquery = (
            self.db.session.query(
                ToDo.habit_id, func.max(ToDo.current_scheduled_date).label("max_date")
            )
            .filter(
                ToDo.user_id == self.user_id,
                ToDo.type == "habit",
                ToDo.current_scheduled_date <= self.today,
                # ToDo.done_date == None,
            )
            .group_by(ToDo.habit_id)
            .subquery()
        )

        latest_scheduled_habits = (
            self.db.session.query(ToDo)
            .join(
                subquery,
                and_(
                    ToDo.habit_id == subquery.c.habit_id,
                    ToDo.current_scheduled_date == subquery.c.max_date,
                ),
            )
            .all()
        )
        return latest_scheduled_habits

    @classmethod
    def from_db(cls):
        scheduler = cls()
        scheduler._set_habits_from_db()
        return scheduler

    def _set_habits_from_db(self):
        habits = Habit.query.all()
        # habits = HabitSchema(many=True).dump(db_habits)
        self.habits = habits
        return self

    # def _set_schedule_from_db(self):
    #     db_schedules = Schedule.query.all()
    #     self.schedules = db_schedules
