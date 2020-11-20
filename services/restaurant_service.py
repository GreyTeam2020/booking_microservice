from app_constant import RESTAURANTS_MICROSERVICE_URL
from utils.http_utils import HttpUtils


class RestaurantService:
    """
    This method contains all the logic to
    interact with Restaurant microservice
    """

    @staticmethod
    def get_tables(restaurant_id: int):
        response = HttpUtils.make_get_request("{}/{}/tables".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
        if response is None:
            return None
        return response["tables"]

    @staticmethod
    def get_openings(restaurant_id: int):
        response = HttpUtils.make_get_request("{}/{}/openings".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
        if response is None:
            return None
        return response["openings"]

    @staticmethod
    def get_info(restaurant_id: int):
        return HttpUtils.make_get_request("{}/{}".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
