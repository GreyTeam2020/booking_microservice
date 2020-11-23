from flask import current_app


class UserModel:

    def fill_from_json(self, json_obj):
        current_app.logger.debug("filling user from: {}".format(json_obj))
        self.email = json_obj["email"]
        self.firstname = json_obj["firstname"]
        self.lastname = json_obj["lastname"]
        self.phone = json_obj["phone"]
        self.is_positive = json_obj["is_positive"]

