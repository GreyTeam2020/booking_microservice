from flask import current_app
from database import Reservation, Friend
from model.opening_hours_model import OpeningHoursModel
import datetime


class Utils:
    """
    This class contains som utils to testing well the system
    """

    @staticmethod
    def reproduce_json_response(message: str, is_custom_obj: bool = False):
        if is_custom_obj is False:
            return {"result": message}
        return message

    @staticmethod
    def create_openings_json():
        return [
            {
                "week_day": 1,
                "open_lunch": "11:30",
                "close_lunch": "15:30",
                "open_dinner": "19:00",
                "close_dinner": "22:00",
                "restaurant_id": "1",
            },
            {
                "week_day": 3,
                "open_lunch": "11:30",
                "close_lunch": "15:30",
                "open_dinner": "19:00",
                "close_dinner": "22:00",
                "restaurant_id": "1",
            },
            {
                "week_day": 5,
                "open_lunch": "11:30",
                "close_lunch": "15:30",
                "open_dinner": "19:00",
                "close_dinner": "22:00",
                "restaurant_id": "1",
            },
        ]

    @classmethod
    def create_tables_json(cls):
        return [
            {
                "id": 1,
                "name": "Table 1",
                "max_seats": 6,
                "available": True,
                "restaurant_id": 1,
            },
            {
                "id": 2,
                "name": "Table 2",
                "max_seats": 4,
                "available": True,
                "restaurant_id": 1,
            },
            {
                "id": 3,
                "name": "Table 3",
                "max_seats": 2,
                "available": True,
                "restaurant_id": 1,
            },
        ]

    @classmethod
    def create_tables_noname_json(cls):
        return [
            {
                "id": 1,
                "name": "Table 1",
                "max_seats": 6,
                "available": True,
                "restaurant_id": 1,
            },
            {
                "id": 2,
                "name": "Table 2",
                "max_seats": 4,
                "available": True,
                "restaurant_id": 1,
            },
            {
                "id": 3,
                "name": "",
                "max_seats": 2,
                "available": True,
                "restaurant_id": 1,
            },
        ]

    @staticmethod
    def insert_reservation(
        py_datetime=datetime.datetime(year=2021, month=4, day=27, hour=12, minute=30),
        avg_time=30,
        people_number=2,
        table_id=3,
        user_id=1,
    ):
        db_session = current_app.config["DB_SESSION"]

        friends_mail = []
        if people_number > 1:
            for n in range(1, people_number):
                friends_mail.append("friend{}@me.com".format(n))

        # register on db the reservation
        new_reservation = Reservation()
        new_reservation.reservation_date = py_datetime
        new_reservation.reservation_end = py_datetime + datetime.timedelta(
            minutes=avg_time
        )
        new_reservation.customer_id = user_id
        new_reservation.table_id = table_id
        new_reservation.people_number = people_number
        db_session.add(new_reservation)
        db_session.flush()
        if people_number > 1:
            for mail in friends_mail:
                new_friend = Friend()
                new_friend.reservation_id = new_reservation.id
                new_friend.email = mail.strip()
                db_session.add(new_friend)
        db_session.commit()

        return new_reservation

    @staticmethod
    def delete_all_reservations():
        db_session = current_app.config["DB_SESSION"]
        all_reservation = db_session.query(Reservation).all()
        for reservation in all_reservation:
            db_session.query(Friend).filter_by(reservation_id=reservation.id).delete()
            db_session.commit()
            db_session.query(Reservation).filter_by(id=reservation.id).delete()
            db_session.commit()

    @staticmethod
    def check_number_of_reseservation():
        db_session = current_app.config["DB_SESSION"]
        return len(db_session.query(Reservation).all())

    @staticmethod
    def create_openings_model():
        openings_json = Utils.create_openings_json()
        openings_model = []
        for opening_json in openings_json:
            opening_model = OpeningHoursModel()
            opening_model.fill_from_json(opening_json)
            openings_model.append(opening_model)

        return openings_model

    @staticmethod
    def openings_json_to_model(openings_json):
        openings_model = []
        for opening_json in openings_json:
            opening_model = OpeningHoursModel()
            opening_model.fill_from_json(opening_json)
            openings_model.append(opening_model)

        return openings_model
