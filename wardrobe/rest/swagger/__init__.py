from urllib.parse import urlparse

from flask import Blueprint, current_app, jsonify, request, url_for
from flask_swagger import swagger

from wardrobe.__meta__ import __api_name__, __version__

swagger_bp = Blueprint("swagger", __name__)


@swagger_bp.route("/spec")
def api_spec():
    swag = swagger(current_app, prefix="/api")

    swag["info"]["config"] = current_app.config.get("CONFIG_NAME")
    swag["info"]["title"] = __api_name__
    swag["info"]["version"] = __version__
    swag["host"] = request.host
    swag["basePath"] = url_for(
        "root",
    ).rstrip("/")

    o = urlparse(url_for("root", _external=True))

    swag["schemes"] = [
        o.scheme,
    ]
    swag["securityDefinitions"] = {
        "Sub": {
            "type": "apiKey",
            "name": "sub",
            "in": "header",
            "description": "Subject Header",
        }
    }

    return jsonify(swag)
