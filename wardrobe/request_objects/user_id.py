import dataclasses

from ca_util import InvalidRequestObject


@dataclasses.dataclass
class UserIdRequestObject:
    user_id: int

    @classmethod
    def from_dict(cls, adict=None, **kwargs):
        if adict is None:
            adict = kwargs

        try:
            user_id = int(adict.get('user_id'))

            return cls(user_id=user_id)
        except ValueError:

            return InvalidRequestObject()
