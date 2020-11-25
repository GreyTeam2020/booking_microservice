from model.user_model import UserModel
from utils.http_utils import HttpUtils
from app_constant import USER_MICROSERVICE_URL


class UserService:
    """
    This service is a wrapper of all operation with users
    """

    @staticmethod
    def get_user_info(user_id: int):
        response = HttpUtils.make_get_request(
            "{}/{}".format(USER_MICROSERVICE_URL, user_id)
        )
        if response is None:
            return HttpUtils.error_message(500, "Can't retrieve info about yourself")

        user = UserModel()
        user.fill_from_json(response)
        return user
