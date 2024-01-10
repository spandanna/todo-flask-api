import datetime as dt

from sqlalchemy import and_, func

from db.database import ToDo


class Scheduler:

    look_ahead_window = 60

    def __init__(self, user_id, db, end_date: dt.date = None, today: dt.date = None):
        self.today = today or dt.date.today()
        self.end_date = end_date or today + dt.timedelta(self.look_ahead_window)
        self.user_id = user_id
        self.db = db
        self.todos = []
        self.habits = []

        self.scheduling_types = {
            "intervalDay": ("intervalType", "day"),
            "intervalWeek": ("intervalType", "weekly"),
            # "intervalMonth": ("intervalType", "monthly"),
        }
        self.habits_by_scheduling_type = []

    def reschedule(self):
        self._reschedule_habits()
        self._reschedule_tasks()
        self.reset_todos()

    def reset_todos(self):
        todos = ToDo.query.filter(
            ToDo.scheduled_date >= self.today,
            ToDo.scheduled_date <= self.end_date,
            ToDo.user_id == self.user_id,
        ).all()

        self.set_todos(todos)

    def set_todos(self, todos):
        self.todos = todos

    def get_todos(self):
        return self.todos

    def _reschedule_tasks(self):
        ToDo.query.filter(
            ToDo.type == "task",
            ToDo.scheduled_date < self.today,
            ToDo.done_date == None,  # noqa: E711 filter doesn't work with `is`
            ToDo.user_id == self.user_id,
        ).update({"scheduled_date": self.today})
        self.db.session.commit()

    def _reschedule_habits(self):
        latest_habits = self._get_latest_scheduled_habits()
        for habit in latest_habits:
            if habit.done_date is None and habit.scheduled_date != self.today:
                habit.scheduled_date = self.today
                self.db.session.commit()

    def _get_latest_scheduled_habits(self):
        # Find the latest scheduled date up until today for each habit
        subquery = (
            self.db.session.query(
                ToDo.habit_id, func.max(ToDo.scheduled_date).label("max_date")
            )
            .filter(
                ToDo.user_id == self.user_id,
                ToDo.type == "habit",
                ToDo.scheduled_date <= self.today,
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
                    ToDo.scheduled_date == subquery.c.max_date,
                ),
            )
            .all()
        )
        return latest_scheduled_habits
