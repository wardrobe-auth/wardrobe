from dataclasses import dataclass


@dataclass
class TokenEntity:
    id: str
    username: str

    def get_user_id(self):
        return self.id

    @classmethod
    def from_dict(cls, a_dict=None, **kwargs):
        if a_dict is None:
            a_dict = kwargs

        return cls(**a_dict)
