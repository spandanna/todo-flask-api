import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    VERSION = "0.1"
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    ENDPOINTS = {
        "/users": ["GET", "POST", "DELETE"],
        "/users/<user_id>": ["GET", "PATCH", "DELETE"],
        "/users/<user_id>/habits": ["GET", "POST", "DELETE"],
        "/users/<user_id>/habits/<habit_id>": ["GET", "PATCH", "DELETE"],
        "/users/<user_id>/todos": ["GET", "POST"],
        "/users/<user_id>/todos/<todo_id>": ["PATCH"],
    }


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI.replace(
        "todo.db", "test.db"
    )
