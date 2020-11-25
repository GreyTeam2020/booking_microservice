class RestaurantModel:
    def fill_from_json(self, json_obj):
        self.avg_time = json_obj["avg_time"]
        self.covid_measures = json_obj["covid_measures"]
        self.id = json_obj["id"]
        self.lat = json_obj["lat"]
        self.lon = json_obj["lon"]
        self.name = json_obj["name"]
        self.owner_email = json_obj["owner_email"]
        self.phone = json_obj["phone"]
        self.rating = json_obj["rating"]
