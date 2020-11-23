import datetime

from services.booking_service import BookingService
from utils.utils_test import Utils


class Test_Units:
    """
    This test include the unit testing that
    help us to test the single functions behaviour
    """
    def test_check_utils_functions(self):
        tables = Utils.create_tables_json()

        Utils.insert_reservation()
        assert Utils.check_number_of_reseservation() == 1
        Utils.delete_all_reservations()
        assert Utils.check_number_of_reseservation() == 0


    def test_filter_openings_ok(self):
        openings = Utils.create_openings_json()

        result = BookingService.filter_openings(openings, week_day=1)
        assert len(result) == 1

    def test_filter_openings_ko(self):
        openings = Utils.create_openings_json()

        result = BookingService.filter_openings(openings, week_day=2)
        assert len(result) == 0


    def test_fitler_table_min_seats_ok(self):
        tables = Utils.create_tables_json()

        result = BookingService.filter_table_min_seat(tables, 2)
        assert len(result) == len(tables)

    def test_fitler_table_min_seats_ko(self):
        tables = Utils.create_tables_json()

        result = BookingService.filter_table_min_seat(tables, 6)
        assert len(result) != len(tables)

    def test_get_table_name_ok(self):
        tables = Utils.create_tables_json()

        result = BookingService.get_table_name(tables, 1)
        assert result == tables[0]["name"]

    def test_get_table_name_noname_ok(self):
        tables = Utils.create_tables_noname_json()

        result = BookingService.get_table_name(tables, 3)
        assert result == "Table #3"

    def test_get_table_name_ko(self):
        tables = Utils.create_tables_json()

        result = BookingService.get_table_name(tables, 4)
        assert result == "NO_NAME"

    def test_get_free_tables_ok(self):
        tables = Utils.create_tables_json()
        Utils.insert_reservation(people_number=2)

        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=12, minute=30)
        free_tables = BookingService.get_free_tables(tables, 4, py_datetime, 30)

        #STILL TWO TABLES FREE
        assert len(free_tables) == 2

        Utils.delete_all_reservations()

    def test_get_free_tables_ko(self):
        tables = Utils.create_tables_json()
        Utils.insert_reservation(people_number=2)
        Utils.insert_reservation(people_number=3, table_id=2)
        Utils.insert_reservation(people_number=5, table_id=1)

        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=12, minute=30)
        free_tables = BookingService.get_free_tables(tables, 4, py_datetime, 30)

        #NO MORE TABLES
        assert len(free_tables) != 1

        Utils.delete_all_reservations()

    def test_get_min_seats_table_ok(self):
        tables = Utils.create_tables_json()

        min_seat_table = BookingService.get_min_seats_table(tables)
        assert min_seat_table == 3

    def test_check_restaurant_openings_ok(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=12, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result == True

    def test_check_restaurant_openings_ko_1(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=12, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)
        #test case: no luch no dinner
        openings[0].open_lunch = None
        openings[0].open_dinner = None

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result[1] == 404

    def test_check_restaurant_openings_ko_2(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=23, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)
        #test case: open dinner but py_datetime > close_dinner
        openings[0].open_lunch = None

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result[1] == 404

    def test_check_restaurant_openings_ko_3(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=17, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)
        #test case: close dinner and py_datetime > close_lunch
        openings[0].close_dinner = None

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result[1] == 404

    def test_check_restaurant_openings_ko_4(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=23, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)
        #test case: always open py_datetime > close_dinner

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result[1] == 404

    def test_check_restaurant_openings_ko_5(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=17, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)
        #test case: always open py_datetime > close_lunch

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result[1] == 404

    def test_check_restaurant_openings_ko_6(self):
        openings = Utils.create_openings_json()
        py_datetime = datetime.datetime(year=2021, month=4, day=27, hour=10, minute=30)

        #filter opening by week_day
        opening = BookingService.filter_openings(openings, py_datetime.weekday())
        assert len (opening) == 1

        #transform opening found in a OpeningHourModel
        openings = Utils.openings_json_to_model(opening)
        #test case: always open py_datetime < open_lunch

        #check if the restaurant is open
        result = BookingService.check_restaurant_openings(openings[0], py_datetime)
        assert result[1] == 404


    def test_reservation_to_json_ok(self):
        reservation = Utils.insert_reservation()
        reservation2 = Utils.insert_reservation(people_number=4)
        all_reservations = [reservation, reservation2]

        json_array = BookingService.reservations_to_json(all_reservations, what="simple")

        assert len(all_reservations) == len(json_array)
