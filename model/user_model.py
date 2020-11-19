

class UserModel:

    def fill_from_json(self, json_obj):
        self.email = json_obj["email"]
        self.firstname = json_obj["firstname"]
        self.lastname = json_obj["lastname"]
        self.is_positive = json_obj["is_positive"]

