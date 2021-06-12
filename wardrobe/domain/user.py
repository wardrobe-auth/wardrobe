from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    username: str
    email: str

    def get_id(self):
        return self.id

    def get_user_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return self.id is None

    @classmethod
    def from_dict(cls, a_dict=None, **kwargs):
        if a_dict is None:
            a_dict = kwargs

        return cls(**a_dict)

    def to_dict(self):
        return dict(id=self.id, username=self.username, email=self.email)
