from ca_util import ResponseFailure, ResponseSuccess

from wardrobe.request_objects.user_id import UserIdRequestObject
from wardrobe.request_objects.user_paginate import UserPaginateRequestObject


class UserDetailUseCase:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, request_object: UserIdRequestObject):
        if not request_object:
            return ResponseFailure.build_from_invalid_request_object(request_object)

        user_id = request_object.user_id
        user = self.user_repo.get(user_id)
        if user is None:
            return ResponseFailure.build_resource_error(f'User:{user_id} not found.')

        return ResponseSuccess(user)
