import datetime as dt

from db.database import ToDo


def get_completion_rate(habit_id: int, start_date: dt.date, end_date: dt.date):
    """
    Gets the proportion of done:scheduled habits over the given period.
    """
    scheduled_todos = ToDo.query.filter(
        ToDo.habit_id == habit_id,
        ToDo.scheduled_date <= end_date,
        ToDo.scheduled_date >= start_date,
    )

    n_scheduled_todos = scheduled_todos.count()
    n_completed_todos = scheduled_todos.filter(
        ToDo.done_date <= end_date, ToDo.scheduled_date >= start_date
    ).count()

    return n_completed_todos / n_scheduled_todos
