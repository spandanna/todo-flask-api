from flask import Blueprint, current_app, make_response
from flask_restx import Api, Resource

root_blueprint = Blueprint("root_blueprint", __name__)
api = Api(root_blueprint, doc="docs")


@api.route("/version")
class version(Resource):
    def get(self):
        return make_response({"version": current_app.config["VERSION"]}, 200)
