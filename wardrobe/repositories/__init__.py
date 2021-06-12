from dataclasses import dataclass, asdict


@dataclass
class PaginationDto:
    page: int
    per_page: int


@dataclass
class PaginationResponse:
    page: int
    per_page: int
    total: int
    total_page: int

    @property
    def has_next(self):
        return self.total_page > self.page

    def to_dict(self):
        return dict(asdict(self), has_next=self.has_next)
