from authlib.oauth2 import OAuth2Error
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
)
from flask_login import current_user

from wardrobe.services.grant import RevocationEndpoint, IntrospectionEndpoint
from wardrobe.services.oauth2 import authorization

oauth2 = Blueprint("oauth2", __name__)


@oauth2.route("/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()


@oauth2.route(
    "/authorize",
    methods=[
        "GET",
    ],
)
def authorize():
    user = current_user
    if user.is_anonymous:
        query_string = dict(
            client_id=request.args.get("client_id", ""),
            response_type=request.args.get("response_type", ""),
            scope=request.args.get("scope", ""),
            redirect_uri=request.args.get("redirect_uri", ""),
            nonce=request.args.get("nonce", ""),
        )
        return_url = url_for("oauth2.authorize", **query_string)

        return redirect(url_for("user.login", next=return_url, reg_next=return_url))

    try:
        grant = authorization.get_consent_grant(end_user=user)
    except OAuth2Error as error:
        return jsonify(dict(error.get_body()))

    return render_template("authorize.html", user=user, grant=grant)


@oauth2.route(
    "/authorize",
    methods=[
        "POST",
    ],
)
def handle_authorize():
    user = current_user

    if user.is_anonymous:
        query_string = dict(
            client_id=request.args.get("client_id", ""),
            response_type=request.args.get("response_type", ""),
            scope=request.args.get("scope", ""),
        )

        return_url = url_for("oauth2.authorize", **query_string)

        return redirect(url_for("main.login", next=return_url))

    if request.form["confirm"]:
        grant_user = user
    else:
        grant_user = None

    return authorization.create_authorization_response(grant_user=grant_user)


@oauth2.route("/revoke", methods=["POST"])
def revoke_token():
    return authorization.create_endpoint_response(RevocationEndpoint.ENDPOINT_NAME)


@oauth2.route("/token/introspect", methods=["POST"])
def introspect_token():
    return authorization.create_endpoint_response(IntrospectionEndpoint.ENDPOINT_NAME)
