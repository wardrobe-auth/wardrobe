from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint, request
from flask import jsonify

from wardrobe.repositories.sqla.models import User
from wardrobe.request_objects.user_id import UserIdRequestObject
from wardrobe.request_objects.user_paginate import UserPaginateRequestObject
from wardrobe.rest.database import db
from wardrobe.rest.proxy import user_repo
from wardrobe.rest.schema import UserSchema
from wardrobe.services.oauth2 import require_oauth
from wardrobe.use_cases.user_detail import UserDetailUseCase
from wardrobe.use_cases.user_paginate import UserPaginateUseCase

api = Blueprint("api", __name__)
admin = Blueprint("admin", __name__)


@api.route("/me")
@require_oauth("profile")
def api_me():
    user_id = current_token.user_id
    user = db.session.query(User).get(user_id)
    rv = dict(
        id=user_id,
        language=user.language,
        country=user.country,
        gender=user.gender,
    )

    return jsonify(rv)


@admin.route("/users")
def user_paginate():
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)
    request_object = UserPaginateRequestObject.from_dict(page=page, per_page=per_page)

    uc = UserPaginateUseCase(user_repo)
    resp = uc.execute(request_object)
    if not resp:
        return jsonify({}), 400

    users, pagination = resp.value

    schema = UserSchema(many=True)
    return jsonify({"data": schema.dump(users), "pagination": pagination.to_dict()})


@admin.route("/users/<user_id>")
def user_detail(user_id):
    request_object = UserIdRequestObject.from_dict(user_id=user_id)

    uc = UserDetailUseCase(user_repo)
    resp = uc.execute(request_object)
    if not resp:
        return jsonify({'message': resp.message}), 404

    user = resp.value

    schema = UserSchema()
    return jsonify({"data": schema.dump(user)})
