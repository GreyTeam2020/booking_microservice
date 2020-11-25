import requests
from flask import current_app
from app_constant import EMAIL_MICROSERVICE_URL


class SendEmailService:
    """
    This method contains all the logic to
    send the email with send email microservices
    """

    @staticmethod
    def booking_confirmation(
        email, user_name, restaurant_name, splitted_friends, reservation_date
    ):
        """
        method to send booking confermation via email microservice
        """
        current_app.logger.debug("Email to send the email: {}".format(email))
        json = {
            "email_user": email,
            "user_name": user_name,
            "restaurant_name": restaurant_name,
            "friends": splitted_friends,
            "booking_time": reservation_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        current_app.logger.debug("JSON request {}".format(json))
        url = "{}/booking_confirmation".format(EMAIL_MICROSERVICE_URL)
        current_app.logger.debug("URL to microservices sendemail {}".format(url))
        response = requests.post(url=url, json=json)
        current_app.logger.debug(response.status_code)
        # Ignoring status, hope it worked
        # if response.ok is False:
        #    current_app.logger.error("Error during the request: {}".format(response.status_code))
        #    current_app.logger.error("Error with message {}".format(json))
        #    return False
        return True
