import logging
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy import or_

from app_constant import RESTAURANTS_MICROSERVICE_URL
from database import Reservation
from model.reservation_customer_model import ReservationCustomerModel
from model.reservation_restaurant_model import ReservationRestaurantModel
from services import UserService
from utils.http_utils import HttpUtils


class BookingService:
    """
    This service is a wrapper of all operation with bookings
    """

    @staticmethod
    def filter_openings(openings, week_day=None):
        if week_day is not None:
            openings = [obj for obj in openings if (obj['week_day'] == week_day)]
        return openings

    @staticmethod
    def filter_table_min_seat(tables, people_number: int):
        table_list = []
        for table in tables:
            if table["max_seats"] >= people_number:
                table_list.append(table)

        return table_list

    @staticmethod
    def get_table_name(tables, table_id: int):
        for table in tables:
            if table["id"] == table_id:
                if table["name"] == "":
                    return "Table #{}".format(table["id"])
                return table["name"]
        return "NO_NAME"

    @staticmethod
    def get_free_tables(tables, people_number: int, py_datetime: datetime, avg_time: int):
        db_session = current_app.config["DB_SESSION"]
        table_list = BookingService.filter_table_min_seat(tables, people_number)
        ints = [table["id"] for table in table_list]

        reservations = (
            db_session.query(Reservation)
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
                .filter(Reservation.table_id.in_(ints))
        ).all()
        booked_tables = [reservation.table_id for reservation in reservations]

        free_tables = []
        for table in table_list:
            if table["id"] not in booked_tables:
                free_tables.append(table)

        return free_tables

    @staticmethod
    def get_min_seats_table(tables):
        min_value = (
            tables[0]["id"],
            tables[0]["max_seats"],
        )
        for i in range(1, len(tables)):
            if tables[i]["max_seats"] < min_value[1]:
                min_value = (
                    tables[i]["id"],
                    tables[i]["max_seats"],
                )

        return min_value[0]

    @staticmethod
    def check_restaurant_openings(opening_hour, py_datetime):
        only_time = py_datetime.time()

        # strange situation.. but it could happen
        # opening hour is in db but the restaurant is closed both lunch and dinner
        if opening_hour.open_lunch is None and opening_hour.open_dinner is None:
            return HttpUtils.error_message(404, "The restaurant is closed")

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
                return HttpUtils.error_message(404, "The restaurant is closed")

        if (opening_hour.open_dinner is None or opening_hour.close_dinner is None) and (
                only_time < opening_hour.open_lunch or only_time > opening_hour.close_lunch
        ):
            return HttpUtils.error_message(404, "The restaurant is closed")

        # if the restaurant is opened both at dinner and lunch
        if opening_hour.open_lunch is not None and opening_hour.open_dinner is not None:
            # asked for some hours outside the opening hours
            if only_time < opening_hour.open_lunch:
                if opening_hour.close_dinner < opening_hour.open_dinner:
                    if only_time > opening_hour.close_dinner:
                        return HttpUtils.error_message(404, "The restaurant is closed")
                else:
                    return HttpUtils.error_message(404, "The restaurant is closed")
            if (
                    only_time < opening_hour.open_dinner
                    and only_time > opening_hour.close_lunch
            ):
                return HttpUtils.error_message(404, "The restaurant is closed")
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
                return HttpUtils.error_message(404, "The restaurant is closed")
        return True

    @staticmethod
    def reservation_to_json(reservation, what="simple"):
        current_app.logger.debug("JSON parse: type={}".format(what))
        current_app.logger.debug("JSON parse: type={}".format(what))

        if what == "simple":
            return {
                "id": reservation.id,
                "reservation_date": reservation.reservation_date,
                "reservation_end": reservation.reservation_end,
                "customer_id": reservation.customer_id,
                "table_id": reservation.table_id,
                "people_number": reservation.people_number,
                "checkin": reservation.checkin,
                "people": reservation.people
            }
        elif what == "restaurant": # pragma: nocover
            return {
                "id": reservation.id,
                "reservation_date": reservation.reservation_date,
                "reservation_end": reservation.reservation_end,
                "customer_id": reservation.customer_id,
                "table": {
                    "id": reservation.table.id,
                    "name": reservation.table.name,
                    "restaurant": {
                        "id": reservation.table.restaurant.id,
                        "name": reservation.table.restaurant.name,
                    }
                },
                "people_number": reservation.people_number,
                "checkin": reservation.checkin,
                "people": reservation.people
            }
        elif what == "customer": # pragma: nocover
            return {
                "id": reservation.id,
                "reservation_date": reservation.reservation_date,
                "reservation_end": reservation.reservation_end,
                "customer": {
                    "firstname": reservation.customer.firstname,
                    "lastname": reservation.customer.lastname,
                    "email": reservation.customer.email,
                    "phone": reservation.customer.phone
                },
                "table": {
                    "id": reservation.table.id,
                    "name": reservation.table.name
                },
                "people_number": reservation.people_number,
                "checkin": reservation.checkin
            }

    @staticmethod
    def reservations_to_json(reservations, what="restaurant"):
        current_app.logger.debug("I'm the translator, i got: {}".format(reservations))
        to_return = []
        for r in reservations:
            to_return.append(BookingService.reservation_to_json(r, what))
        current_app.logger.debug(to_return)
        return to_return

    @staticmethod
    def replace_with_restaurant(reservation): # pragma: nocover
        response = HttpUtils.make_get_request("{}/table/{}".format(RESTAURANTS_MICROSERVICE_URL, reservation.table_id))

        current_app.logger.debug("ok, adding")
        r2 = ReservationRestaurantModel()
        r2.fill_from_Reservation(reservation)

        r2.addTable(response)
        current_app.logger.debug("added")
        return r2

    @staticmethod
    def replace_with_customer(reservation): # pragma: nocover
        response = HttpUtils.make_get_request("{}/table/{}".format(RESTAURANTS_MICROSERVICE_URL, reservation.table_id))

        current_app.logger.debug("ok, adding")
        r2 = ReservationCustomerModel()
        r2.fill_from_Reservation(reservation)

        r2.addTable(response)
        current_app.logger.debug("added table")

        customer = UserService.get_user_info(reservation.customer_id)
        r2.addCustomer(customer)
        return r2
