from flask import Flask, current_app

from db.database import db, migrate


def create_app(app_config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(app_config)

    from core.api import blueprint as api

    app.register_blueprint(api, url_prefix="/api/v1")
    # @app.route(v1)
    # def home():
    #     return {"version": app.config["VERSION"]}

    db.init_app(app)
    migrate.init_app(app, db)

    return app
