import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

NUMBER_OF_DAYS_ADDED = timedelta(days=1)
MONTHS_INTERVAL = relativedelta(months=6)


class FlightData:

    def __init__(self):
        self.date = datetime.now().date()
        self.tomorrow = self.date + NUMBER_OF_DAYS_ADDED

        self.date_from = self.tomorrow
        self.date_to = self.date_from + MONTHS_INTERVAL
