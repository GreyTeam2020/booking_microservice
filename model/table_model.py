from model.restaurant_model import RestaurantModel


class TableModel:
    def fill_from_json(self, json_obj):
        self.available = json_obj["available"]
        self.id = json_obj["id"]
        self.max_seats = json_obj["max_seats"]
        self.name = json_obj["name"]

        restaurant = RestaurantModel()
        restaurant.fill_from_json(json_obj["restaurant"])
        self.restaurant = restaurant
