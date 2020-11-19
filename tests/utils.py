from datetime import datetime, timedelta
from random import randrange

from sqlalchemy import or_

import app
from database import Reservation, Friend
from model.opening_hours_model import OpeningHoursModel
from services.user_service import UserService
from services.booking_service import BookingService
from services.restaurant_service import RestaurantService
from services.send_email_service import SendEmailService
from app import db_session

class Utils:
    """
    This class contains all logic to implement the client request
    to make a simple component test.
    """

    @staticmethod
    def reproduce_json_response(message: str, is_custom_obj: bool = False):
        if is_custom_obj is False:
            return {"result": message}
        return message
