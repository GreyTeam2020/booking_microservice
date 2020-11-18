import logging
from datetime import datetime
from database import User, Role


class BookingService:
    """
    This service is a wrapper of all operation with bookings
    """

    def filter_openings(self, openings, week_day=None):
        if week_day is not None:
            openings = [obj for obj in openings if (obj['type'] == 1)]

        return openings
