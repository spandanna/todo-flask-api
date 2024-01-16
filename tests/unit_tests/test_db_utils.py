import datetime as dt

from db.database import ToDo, db
from utils.db_utils import get_completion_rate


def test_get_completion_rate(new_user_with_habits, app_fixture):
    """
    Tests that get_completion_rate returns floats and expected values.
    """
    new_user_with_habits(
        habit_dicts=[
            {
                "name": "lazy habit",
                "interval_type": "day",
                "interval_value": 2,
                "start_date": dt.date.today() - dt.timedelta(days=7),
            }
        ]
    )
    with app_fixture.app_context():
        cr = get_completion_rate(
            1, dt.date.today() - dt.timedelta(days=7), dt.date.today()
        )

    assert isinstance(cr, float)
    assert cr == 0.0

    with app_fixture.app_context():
        scheduled_habit = ToDo.query.filter(ToDo.name == "lazy habit").first()
        scheduled_habit.done_date = dt.date.today()
        db.session.commit()
        cr = get_completion_rate(
            1, dt.date.today() - dt.timedelta(days=7), dt.date.today()
        )

    assert isinstance(cr, float)
    assert cr == 0.25
