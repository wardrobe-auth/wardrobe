import dataclasses

from wardrobe.repositories import PaginationDto


@dataclasses.dataclass
class UserPaginateRequestObject:
    pagination: PaginationDto

    @classmethod
    def from_dict(cls, adict=None, **kwargs):
        if adict is None:
            adict = kwargs

        pagination = PaginationDto(
            page=adict.get("page", 1),
            per_page=adict.get("per_page", 10),
        )

        return cls(pagination=pagination)
