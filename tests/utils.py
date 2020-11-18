from datetime import datetime, timedelta
from random import randrange

from sqlalchemy import or_

import app
from database import Reservation, Friend
from model.opening_hours_model import OpeningHoursModel
from services import BookingService
from services.send_email_service import SendEmailService
from utils.http_utils import HttpUtils
from app_constant import *
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

    @staticmethod
    def book(restaurant_id, current_user, py_datetime, people_number, raw_friends):

        # split friends mail and check if the number is correct
        if people_number > 1:
            splitted_friends = raw_friends.split(";")
            if len(splitted_friends) != (people_number - 1):
                app.error_message(400, "You need to specify ONE mail for each person")

        restaurant_id = int(restaurant_id)

        # if user wants to book in the past..
        if py_datetime < datetime.now():
            app.error_message(400, "You can not book in the past!")

        # check if the user is positive
        is_positive = False #TODO: serve endpoint in User
        if is_positive:
            app.error_message(401, "You are marked as positive!")

        week_day = py_datetime.weekday()
        only_time = py_datetime.time()

        # check if the restaurant is open. 12 in open_lunch means open at lunch. 20 in open_dinner means open at dinner.
        response = HttpUtils.make_get_request("{}/{}/openings".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
        if response is None:
            app.error_message(500, "Can't retrieve opening hours")

        opening_hour = BookingService.filter_openings(week_day=week_day)[0]

        # the restaurant is closed
        if len(opening_hour) == 0:
            print("No Opening hour")
            app.error_message(404, "The restaurant is closed")

        #bind to obj
        opening_hour = OpeningHoursModel()
        opening_hour.fill_from_json(opening_hour)

        # strange situation.. but it could happen
        # opening hour is in db but the resturant is closed both lunch and dinner
        if opening_hour.open_lunch is None and opening_hour.open_dinner is None:
            app.error_message(404, "The restaurant is closed")

        # if the restaurant is open only at lunch or at dinner do some checks..
        if opening_hour.open_lunch is None or opening_hour.close_lunch is None:
            # calc the projection (py_datetime.date combined with opening hour)

            open_dinner_projection = datetime.combine(
                py_datetime.date(), opening_hour.open_dinner
            )
            if opening_hour.close_dinner < opening_hour.open_dinner:
                close_dinner_projection = datetime.combine(
                    py_datetime.date() + timedelta(days=1),
                    opening_hour.close_dinner,
                )
            else:
                close_dinner_projection = datetime.combine(
                    py_datetime.date(), opening_hour.close_dinner
                )

            if (
                    py_datetime > close_dinner_projection
                    or py_datetime < open_dinner_projection
            ):
                app.error_message(404, "The restaurant is closed")

        if (opening_hour.open_dinner is None or opening_hour.close_dinner is None) and (
                only_time < opening_hour.open_lunch or only_time > opening_hour.close_lunch
        ):
            app.error_message(404, "The restaurant is closed")
        #

        # if the restaurant is opened both at dinner and lunch
        if opening_hour.open_lunch is not None and opening_hour.open_dinner is not None:
            # asked for some hours outside the opening hours
            if only_time < opening_hour.open_lunch:
                if opening_hour.close_dinner < opening_hour.open_dinner:
                    if only_time > opening_hour.close_dinner:
                        app.error_message(404, "The restaurant is closed")
                else:
                    app.error_message(404, "The restaurant is closed")

            if (
                    only_time < opening_hour.open_dinner
                    and only_time > opening_hour.close_lunch
            ):
                app.error_message(404, "The restaurant is closed")

            if opening_hour.close_dinner < opening_hour.open_dinner:
                close_dinner_projection = datetime.combine(
                    py_datetime.date() + timedelta(days=1),
                    opening_hour.close_dinner,
                )
            else:
                close_dinner_projection = datetime.combine(
                    py_datetime.date(), opening_hour.close_dinner
                )

            if py_datetime > close_dinner_projection:
                app.error_message(404, "The restaurant is closed")
            #

        # now let's see if there is a table

        """
        get the time delta (avg_time) from the restaurant table
        """
        response = HttpUtils.make_get_request("{}/{}".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
        if response is None:
            app.error_message(500, "Can't retrive restaurant info")
        restaurant_name = response["name"]
        avg_time = response["avg_time"]

        """
        get all the reservation (with the reservation_date between the dates in which I want to book)
        or (or the reservation_end between the dates in which I want to book)
        the dates in which I want to book are:
        start = py_datetime  
        end = py_datetime + avg_time
        always filtered by the people_number  
        """

        # from the list of all tables in the restaurant (the ones in which max_seats < number of people requested) drop the reserved ones
        response = HttpUtils.make_get_request("{}/{}/tables".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
        if response is None:
            app.error_message(500, "Can't retrieve restaurant tables")
        #model
        all_table_list = []
        table_list = filter_table_min_seat(all_table_list, people_number)

        reservations = (
            db_session.session.query(Reservation)
                .filter(
                or_(
                    Reservation.reservation_date.between(
                        py_datetime, py_datetime + timedelta(minutes=avg_time)
                    ),
                    Reservation.reservation_end.between(
                        py_datetime, py_datetime + timedelta(minutes=avg_time)
                    ),
                )
            )
            .filter(Reservation.table_id.in_(table_list))
        ).all()

        booked_tables = [reservation.table_id for reservation in reservations]

        all_restaurant_tables = list(set(table_list) - set(booked_tables))

        # if there are tables available.. get the one with minimum max_seats
        print("OK, There are {} tables available".format(len(all_restaurant_tables)))
        if len(all_restaurant_tables) > 0:
            min_value = (
                all_restaurant_tables[0].id,
                all_restaurant_tables[0].max_seats,
            )
            for i in range(1, len(all_restaurant_tables)):
                if all_restaurant_tables[i].max_seats < min_value[1]:
                    min_value = (
                        all_restaurant_tables[i].id,
                        all_restaurant_tables[i].max_seats,
                    )

            # get table name
            #TODO: is it necessary to do another HTTP request? Mybe retrive it form all_restaurant_tables
            table_name = "TABLE_NAME_NOT_IMPLEMENTED"

            # register on db the reservation
            new_reservation = Reservation()
            new_reservation.reservation_date = py_datetime
            new_reservation.reservation_end = py_datetime + datetime.timedelta(
                minutes=avg_time
            )
            new_reservation.customer_id = current_user.id
            new_reservation.table_id = min_value[0]
            new_reservation.people_number = people_number
            db_session.session.add(new_reservation)
            db_session.session.flush()

            if people_number > 1:
                # register friends
                for friend_mail in splitted_friends:
                    new_friend = Friend()
                    new_friend.reservation_id = new_reservation.id
                    new_friend.email = friend_mail.strip()
                    db_session.session.add(new_friend)
            else:
                splitted_friends = []
            db_session.session.commit()


            #TODO: mancano tutte le info sull'utente
            #SendEmailService.booking_confirmation()
            #DispatcherMessage.send_message(
            #    CONFIRMATION_BOOKING,
            #    [
            #        current_user.email,
            #        current_user.email,
            #        restaurant_name,
            #        splitted_friends,
            #        new_reservation.reservation_date,
            #    ],
            #)
            return {"id": new_reservation, "restaurant_name": restaurant_name, "table_name": table_name}
        else:
            app.error_message(404, "No tables available")