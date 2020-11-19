

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
