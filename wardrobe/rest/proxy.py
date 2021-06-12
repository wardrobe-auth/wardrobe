from werkzeug.local import LocalProxy

from wardrobe.rest.database import db
from wardrobe.repositories.sqla.user import UserRepository

_user_repo = None


def get_repo():
    global _user_repo

    if _user_repo is None:
        _user_repo = UserRepository(db=db)

    return _user_repo


# noinspection PyTypeChecker
user_repo: UserRepository = LocalProxy(get_repo)
