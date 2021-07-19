import time

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2TokenMixin,
    OAuth2AuthorizationCodeMixin,
)
from flask_user import UserMixin
from sqlalchemy.orm import backref

from wardrobe.webapp.database import db
from wardrobe.domain.user import UserEntity


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = "oauth2_client"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
    )


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = "oauth2_code"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
    )


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = "oauth2_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
    )

    def get_nonce(self):
        return None

    def get_auth_time(self):
        return None

    def is_refresh_token_expired(self):
        return time.time() > (self.issued_at + self.expires_in + 60 * 24 * 30)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column("is_active", db.Boolean(), nullable=False, server_default="1")

    # User authentication information. The  is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(
        db.String(
            255,
        ),
        nullable=True,
        unique=False,
    )
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default="")

    # User information
    first_name = db.Column(
        db.String(
            100,
        ),
        nullable=False,
        server_default="",
    )
    last_name = db.Column(
        db.String(
            100,
        ),
        nullable=False,
        server_default="",
    )
    gender = db.Column(
        db.String(
            100,
        ),
        nullable=True,
        server_default=None,
    )
    language = db.Column(
        db.String(
            2,
        ),
        nullable=True,
        server_default=None,
    )
    country = db.Column(
        db.String(
            255,
        ),
        nullable=True,
        server_default=None,
    )

    # Define the relationship to Role via UserRoles
    roles = db.relationship("Role", secondary="user_roles")

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

    def get_user_id(self):
        return self.id

    def get_id(self):
        return self.id

    @classmethod
    def get_user_by_token(cls, token):
        return db.session.query(cls).get(token)

    def to_entity(self):
        return UserEntity.from_dict(
            id=self.id,
            username=self.email,
            email=self.email,
        )


# Define the Role data-model
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))


class Connection(db.Model):
    __tablename__ = "connections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship("User", backref=backref("connections"))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)

    def __repr__(self):
        return f"<Connection:{self.id} {self.provider_id}>"
