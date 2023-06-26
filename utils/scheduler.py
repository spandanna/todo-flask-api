from datetime import datetime, timedelta, date
from typing import List
from db.database import Habit, ToDo
from db.schemas import HabitSchema


class Scheduler:
    def __init__(self):
        self.schedule = {}
        self.habits = []
        self.today = date.today()
        self.scheduling_types = {
            "intervalDaily": ("intervalType", "day"),
            "intervalWeekly": ("intervalType", "weekly"),
            "intervalMonthly": ("intervalType", "monthly"),
        }
        self.habits_by_scheduling_type = []

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

    def _set_schedule_from_db(self):
        db_schedules = Schedule.query.all()
        self.schedules = db_schedules
