from ca_util import ResponseFailure, ResponseSuccess

from wardrobe.request_objects.user_paginate import UserPaginateRequestObject


class UserPaginateUseCase:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, request_object: UserPaginateRequestObject):
        if not request_object:
            return ResponseFailure.build_from_invalid_request_object(request_object)

        items, pagination = self.user_repo.paginate(
            pagination=request_object.pagination
        )

        return ResponseSuccess([items, pagination])
