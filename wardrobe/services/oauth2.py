from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.integrations.sqla_oauth2 import create_bearer_token_validator

from wardrobe.rest.database import db
from wardrobe.services.grant import (
    AuthorizationCodeGrant,
    ResourceOwnerPasswordCredentialsGrant,
    RefreshTokenGrant,
    OpenIDCode,
    RevocationEndpoint,
    IntrospectionEndpoint,
)
from wardrobe.repositories.sqla.models import OAuth2Client, OAuth2Token

authorization = AuthorizationServer()
require_oauth = ResourceProtector()


def query_client(client_id):
    return db.session.query(OAuth2Client).filter_by(client_id=client_id).first()


def save_token(token_data, request):
    if request.user:
        user_id = request.user.get_user_id()
    else:
        # client_credentials grant_type
        user_id = request.client.user_id
        # or, depending on how you treat client_credentials
        user_id = None
    token = OAuth2Token(
        client_id=request.client.client_id, user_id=user_id, **token_data
    )
    db.session.add(token)
    db.session.commit()


def config_oauth(app):
    authorization.init_app(app, query_client=query_client, save_token=save_token)

    # support all openid grants
    authorization.register_grant(
        AuthorizationCodeGrant,
        [
            OpenIDCode(require_nonce=True),
        ],
    )

    authorization.register_grant(
        ResourceOwnerPasswordCredentialsGrant,
        [
            OpenIDCode(require_nonce=False),
        ],
    )

    authorization.register_grant(
        RefreshTokenGrant,
        [
            OpenIDCode(require_nonce=True),
        ],
    )

    authorization.register_endpoint(RevocationEndpoint)

    authorization.register_endpoint(IntrospectionEndpoint)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
