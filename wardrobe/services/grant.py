import dataclasses
import time

from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7009 import RevocationEndpoint as _RevocationEndpoint
from authlib.oauth2.rfc7662 import IntrospectionEndpoint as _IntrospectionEndpoint
from authlib.oidc import core
from authlib.oidc.core import UserInfo
from flask import current_app
from werkzeug.local import LocalProxy
from werkzeug.security import gen_salt

from wardrobe.webapp.database import db
from wardrobe.repositories.sqla.models import (
    User,
    OAuth2AuthorizationCode,
    OAuth2Token,
)
from wardrobe.webapp.user_manager import user_manager


@dataclasses.dataclass
class JwtConfig:
    key: str
    alg: str
    iss: str
    exp: int


def get_jwt_config():
    return JwtConfig(
        key=current_app.config.get("OAUTH2_JWT_SECRET_KEY"),
        alg=current_app.config.get("OAUTH2_JWT_ALG", "RS512"),
        iss=current_app.config.get("OAUTH2_JWT_ISS"),
        exp=int(current_app.config.get("OAUTH2_JWT_EXP", 3600)),
    )


# noinspection PyTypeChecker
current_jwt_config: JwtConfig = LocalProxy(get_jwt_config)


def exists_nonce(nonce, req):
    exists = (
        db.session.query(OAuth2AuthorizationCode)
        .filter_by(client_id=req.client_id, nonce=nonce)
        .first()
    )
    return bool(exists)


def generate_user_info(user, scope):
    return UserInfo(sub=str(user.id), name=user.email)


def create_authorization_code(client, grant_user, request):
    code = gen_salt(48)
    nonce = request.data.get("nonce")
    client_id = client.client_id
    redirect_uri = request.redirect_uri
    scope = request.scope
    user_id = grant_user.id

    item = OAuth2AuthorizationCode(
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        user_id=user_id,
        nonce=nonce,
    )
    db.session.add(item)
    db.session.commit()
    return code


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        client = request.client
        nonce = request.data.get("nonce")
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            nonce=nonce,
        )
        db.session.add(auth_code)
        db.session.commit()
        return auth_code

    def query_authorization_code(self, code, client):
        item = (
            db.session.query(OAuth2AuthorizationCode)
            .filter_by(code=code, client_id=client.client_id)
            .first()
        )
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return db.session.query(User).get(authorization_code.user_id)


class ResourceOwnerPasswordCredentialsGrant(
    grants.ResourceOwnerPasswordCredentialsGrant
):
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post"]

    def authenticate_user(self, username, password):
        user = db.session.query(User).filter_by(email=username).first()
        if user is not None and user_manager.verify_password(password, user.password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    INCLUDE_NEW_REFRESH_TOKEN = True
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post"]

    def revoke_old_credential(self, credential):
        credential.revoked = True
        db.session.add(credential)
        db.session.commit()

    def authenticate_refresh_token(self, refresh_token):
        token = (
            db.session.query(OAuth2Token)
            .filter_by(
                refresh_token=refresh_token,
                revoked=False,
            )
            .first()
        )
        if token and not token.is_refresh_token_expired():
            return token

    def authenticate_user(self, credential):
        return db.session.query(User).get(credential.user_id)


class OpenIDCode(core.OpenIDCode):
    def exists_nonce(self, nonce, request):
        exists = (
            db.session.query(OAuth2AuthorizationCode)
            .filter_by(client_id=request.client_id, nonce=nonce)
            .first()
        )
        return bool(exists)

    def get_jwt_config(self, grant):
        return {
            "key": current_jwt_config.key,
            "alg": current_jwt_config.alg,
            "iss": current_jwt_config.iss,
            "exp": current_jwt_config.exp,
        }

    def generate_user_info(self, user, scope):
        user_info = UserInfo(sub=user.id, name=user.email)
        if "email" in scope:
            user_info["email"] = user.email
        return user_info


class ImplicitGrant(core.OpenIDImplicitGrant):
    def exists_nonce(self, nonce, request):
        # return exists_nonce(nonce, request)
        exists = (
            db.session.query(OAuth2AuthorizationCode)
            .filter_by(client_id=request.client_id, nonce=nonce)
            .first()
        )
        return bool(exists)

    def get_jwt_config(self):
        return {
            "key": current_jwt_config.key,
            "alg": current_jwt_config.alg,
            "iss": current_jwt_config.iss,
            "exp": current_jwt_config.exp,
        }

    def generate_user_info(self, user, scope):
        # return generate_user_info(user, scope)
        user_info = UserInfo(sub=user.id, name=user.name)
        if "email" in scope:
            user_info["email"] = user.email
        return user_info


class HybridGrant(core.OpenIDHybridGrant):
    def save_authorization_code(self, code, request):
        nonce = request.data.get("nonce")
        item = OAuth2AuthorizationCode(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            nonce=nonce,
        )
        db.session.add(item)
        db.session.commit()
        return code

    def exists_nonce(self, nonce, request):
        exists = (
            db.session.query(OAuth2AuthorizationCode)
            .filter_by(client_id=request.client_id, nonce=nonce)
            .first()
        )
        return bool(exists)

    def get_jwt_config(self):
        return {
            "key": current_jwt_config.key,
            "alg": current_jwt_config.alg,
            "iss": current_jwt_config.iss,
            "exp": current_jwt_config.exp,
        }

    def generate_user_info(self, user, scope):
        user_info = UserInfo(sub=user.id, name=user.name)
        if "email" in scope:
            user_info["email"] = user.email
        return user_info


class RevocationEndpoint(_RevocationEndpoint):
    def query_token(self, token_string, token_type_hint):
        query = db.session.query(OAuth2Token)

        if token_type_hint == "access_token":
            return query.filter_by(access_token=token_string).first()
        elif token_type_hint == "refresh_token":
            return query.filter_by(refresh_token=token_string).first()
        # without token_type_hint
        item = query.filter_by(access_token=token_string).first()
        if item:
            return item
        return query.filter_by(refresh_token=token_string).first()

    def revoke_token(self, token, request):
        hint = request.form.get("token_type_hint")
        if hint == "access_token":
            token.access_token_revoked = True
        else:
            token.access_token_revoked = True
            token.refresh_token_revoked = True

        db.session.add(token)
        db.session.commit()


class IntrospectionEndpoint(_IntrospectionEndpoint):
    def check_permission(self, token, client, request):
        return True

    def introspect_token(self, token: OAuth2Token):
        active = self.is_token_active(token)
        user = db.session.query(User).get(token.user_id)
        return {
            "active": active,
            "client_id": token.client_id,
            "token_type": token.token_type,
            "username": user.email,
            "scope": token.get_scope(),
            "sub": user.id,
            "aud": token.client_id,
            "iss": current_jwt_config.iss,
            "exp": (token.issued_at + token.expires_in),
            "iat": token.issued_at,
        }

    def query_token(self, token_string, token_type_hint):
        if token_type_hint == "access_token":
            token = (
                db.session.query(OAuth2Token)
                .filter_by(access_token=token_string)
                .first()
            )
        elif token_type_hint == "refresh_token":
            token = (
                db.session.query(OAuth2Token)
                .filter_by(refresh_token=token_string)
                .first()
            )
        else:
            # without token_type_hint
            token = (
                db.session.query(OAuth2Token)
                .filter_by(access_token=token_string)
                .first()
            )
            if not token:
                token = (
                    db.session.query(OAuth2Token)
                    .filter_by(refresh_token=token_string)
                    .first()
                )
        if token:
            return token

    def is_token_active(self, token: OAuth2Token) -> bool:
        return not token.is_revoked() and not token.is_expired()
