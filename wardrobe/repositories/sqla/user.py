import math
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

from wardrobe.repositories import PaginationDto, PaginationResponse
from wardrobe.repositories.sqla.models import User


class UserRepository:
    def __init__(self, db=None):
        self.db = db
        self.cls = User

    @property
    def session_context(self):
        if self.db:

            @contextmanager
            def session_scope():
                yield self.db.session

        else:

            @contextmanager
            def session_scope():
                Session = sessionmaker(bind=self.engine)
                session = Session()
                try:
                    yield session
                    session.commit()
                except:
                    session.rollback()
                    raise
                finally:
                    session.close()

        return session_scope

    def list(self):
        with self.session_context() as session:
            qry = session.query(self.cls)
            items = qry.all()

        return [item.to_entity() for item in items]

    def paginate(
        self,
        pagination: PaginationDto,
    ):
        page = pagination.page
        per_page = pagination.per_page
        offset = (page - 1) * per_page

        with self.session_context() as session:
            query = session.query(self.cls)
            total = query.count()
            total_page = math.ceil(total / per_page)
            items = query.limit(per_page).offset(offset)
            pagination = PaginationResponse(
                page=page,
                per_page=per_page,
                total=total,
                total_page=total_page,
            )

        return [item.to_entity() for item in items], pagination

    def get(self, id_):
        with self.session_context() as session:
            item = session.query(self.cls).get(id_)
            if item is not None:
                return item.to_entity()

    def create(self, **kwargs):
        with self.session_context() as session:
            item = self.cls(**kwargs)
            session.add(item)
            session.commit()

        return item.to_entity()

    def update(self, id_: int, **kwargs):
        with self.session_context() as session:
            item = session.query(self.cls).get(id_)
            for key, value in kwargs.items():
                setattr(item, key, value)

            session.add(item)
            session.commit()

        return item.to_entity()

    def remove(self, id_: int) -> bool:
        with self.session_context() as session:
            item = session.query(self.cls).get(id_)
            if not item:
                return False

            session.delete(item)
            session.commit()

        return True
