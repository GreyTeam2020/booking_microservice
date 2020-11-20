from datetime import datetime

from flask import current_app


class OpeningHoursModel:

    def fill_from_json(self, json_obj):
        self.close_dinner = datetime.strptime(json_obj["close_dinner"], "%H:%M").time()
        self.close_lunch = datetime.strptime(json_obj["close_lunch"], "%H:%M").time()
        self.open_dinner = datetime.strptime(json_obj["open_dinner"], "%H:%M").time()
        self.open_lunch = datetime.strptime(json_obj["open_lunch"], "%H:%M").time()
        self.restaurant_id = json_obj["restaurant_id"]
        self.week_day = json_obj["week_day"]