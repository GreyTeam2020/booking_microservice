import decimal
import json
import os
from datetime import datetime, timedelta

import connexion
from flask import request, current_app

from database import init_db, Reservation, Friend
import logging

from model.opening_hours_model import OpeningHoursModel
from services.user_service import UserService
from services.booking_service import BookingService
from services.restaurant_service import RestaurantService
from services.send_email_service import SendEmailService
from utils.http_utils import HttpUtils

db_session = None


def _get_response(message: str, code: int, is_custom_obj: bool = False):
    """
    This method contains the code to make a new response for flask view
    :param message: Message response
    :param code: Code result
    :return: a json object that look like {"result": "OK"}
    """
    if is_custom_obj is False:
        return {"result": message}, code
    return message, code

def create_booking():
    json = request.get_json()
    current_app.logger.debug("Request received: {}".format(json))
    restaurant_id = json["restaurant_id"]
    user_id = json["user_id"]
    raw_friends = json["raw_friends"]
    py_datetime = datetime.strptime(json["datetime"], "%Y-%m-%dT%H:%M:%SZ")
    people_number = json["people_number"]
    current_app.logger.debug("Translated obj to vars")
    # split friends mail and check if the number is correct
    if people_number > 1:
        splitted_friends = raw_friends.split(";")
        if len(splitted_friends) != (people_number - 1):
            return HttpUtils.error_message(400, "You need to specify ONE mail for each person")
    current_app.logger.debug("Friends: {}".format(str(splitted_friends)))
    # if user wants to book in the past..
    if py_datetime < datetime.now():
        return HttpUtils.error_message(400, "You can not book in the past!")

    # check if the user is positive
    current_user = UserService.get_user_info(user_id)
    if current_user.is_positive:
        HttpUtils.error_message(401, "You are marked as positive!")
    week_day = py_datetime.weekday()

    # check if the restaurant is open. 12 in open_lunch means open at lunch. 20 in open_dinner means open at dinner.
    openings = RestaurantService.get_openings(restaurant_id)
    current_app.logger.debug("Got {} openings".format(len(openings)))
    # the restaurant is closed
    if openings is None or len(openings) == 0:
        current_app.logger.debug("No open hours")
        return HttpUtils.error_message(404, "The restaurant is closed")

    opening_hour_json = BookingService.filter_openings(openings, week_day=week_day)[0]
    current_app.logger.debug("Got openings this day: {}".format(opening_hour_json))
    # the restaurant is closed
    if opening_hour_json is None: #TODO: Test
        print("No Opening hour")
        return HttpUtils.error_message(404, "The restaurant is closed")

    # bind to obj
    opening_hour = OpeningHoursModel()
    opening_hour.fill_from_json(opening_hour_json)
    current_app.logger.debug("Binded, weekday: {}".format(str(opening_hour.week_day)))

    # check if restaurant is open
    response = BookingService.check_restaurant_openings(opening_hour, py_datetime)
    current_app.logger.debug("Restaurant checked, i got: {}".format(str(response)))
    if response is not True:
        return response
    # now let's see if there is a table
    """
    get the time delta (avg_time) e name from the restaurant
    """
    restaurant_info = RestaurantService.get_info(restaurant_id)
    restaurant_name = restaurant_info["name"]
    avg_time = restaurant_info["avg_time"]

    """
    get all the reservation (with the reservation_date between the dates in which I want to book)
    or (or the reservation_end between the dates in which I want to book)
    the dates in which I want to book are:
    start = py_datetime  
    end = py_datetime + avg_time
    always filtered by the people_number  
    """

    # from the list of all tables in the restaurant (the ones in which max_seats < number of people requested)
    # drop the reserved ones
    all_table_list = RestaurantService.get_tables(restaurant_id)
    if all_table_list is None:
        return HttpUtils.error_message(500, "Can't retrieve restaurant tables")

    free_tables = BookingService.get_free_tables(all_table_list, people_number, py_datetime, avg_time)

    # if there are tables available.. get the one with minimum max_seats
    current_app.logger.debug("OK, There are {} tables available".format(len(free_tables)))
    if len(free_tables) > 0:
        chosen_table = BookingService.get_min_seats_table(free_tables)
        current_app.logger.debug("OK, table {} has been chosen".format(chosen_table))
        # get table name
        table_name = BookingService.get_table_name(all_table_list, chosen_table)
        current_app.logger.debug("His name is: {}".format(table_name))
        # register on db the reservation
        new_reservation = Reservation()
        new_reservation.reservation_date = py_datetime
        new_reservation.reservation_end = py_datetime + timedelta(minutes=avg_time)
        new_reservation.customer_id = user_id
        new_reservation.table_id = chosen_table
        new_reservation.people_number = people_number
        db_session.add(new_reservation)
        db_session.flush()
        current_app.logger.debug("Reservation saved.")
        if people_number > 1:
            # register friends
            for friend_mail in splitted_friends:
                new_friend = Friend()
                new_friend.reservation_id = new_reservation.id
                new_friend.email = friend_mail.strip()
                db_session.add(new_friend)
        else:
            splitted_friends = []
        db_session.commit()

        SendEmailService.booking_confirmation(current_user.email, current_user.firstname, restaurant_name, splitted_friends, new_reservation.reservation_date)

        return {"id": new_reservation.id, "restaurant_name": restaurant_name, "table_name": table_name}, 200
    else:
        return HttpUtils.error_message(404, "No tables available")

def delete_booking(reservation_id, user_id):
    query = (
        db_session.query(Reservation)
            .filter_by(id=reservation_id)
            .filter_by(customer_id=user_id)
    )

    to_delete = query.first()
    if to_delete is None:
        return HttpUtils.error_message(404, "Reservation not Found")

    query.delete()
    db_session.commit()
    return {"code": 200, "message": "Deleted Successfully"}, 200


def get_booking(reservation_id):
    reservation = (
        db_session.query(Reservation)
            .filter_by(id=reservation_id)
            .first()
    )

    if reservation is None:
        return HttpUtils.error_message(404, "Reservation not Found")

    return BookingService.Reservation2JSON(reservation), 200


def get_all_bookings():
    reservations = db_session.query(Reservation).all()

    if reservations is None:
        return HttpUtils.error_message(404, "No Reservations")

    return BookingService.Reservations2JSON(reservations), 200

# --------- END API definition --------------------------
logging.basicConfig(level=logging.DEBUG)
app = connexion.App(__name__)

application = app.app
if "GOUOUTSAFE_TEST" in os.environ and os.environ["GOUOUTSAFE_TEST"] == "1":
    db_session = init_db("sqlite:///tests/booking.db")
else:
    db_session = init_db("sqlite:///db/booking.db")
app.add_api("swagger.yml")


def _init_flask_app(flask_app, conf_type: str = "config.DebugConfiguration"):
    """
    This method init the flask app
    :param flask_app:
    """
    flask_app.config.from_object(conf_type)
    flask_app.config["DB_SESSION"] = db_session


@application.teardown_appcontext
def shutdown_session(exception=None):
    if db_session is not None:
        db_session.remove()


if __name__ == "__main__":
    _init_flask_app(application)
    app.run(port=5004)
