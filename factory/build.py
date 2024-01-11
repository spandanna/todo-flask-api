from flask import Flask

from db.database import db, migrate


def create_app(app_config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(app_config)

    from core.root import root_blueprint
    from core.users import users_blueprint

    app.register_blueprint(users_blueprint, url_prefix="/api/v1")
    app.register_blueprint(root_blueprint, url_prefix="/api")

    db.init_app(app)
    migrate.init_app(app, db)
    return app
