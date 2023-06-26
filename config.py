from dotenv import load_dotenv
import os

load_dotenv()


class Config(object):
    VERSION = "0.1"
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI.replace(
        "todo.db", "test.db"
    )
