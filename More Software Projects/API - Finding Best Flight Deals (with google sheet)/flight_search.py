import requests
from flight_data import FlightData
from data_manager import DataManager

flight_details = FlightData()
data_mgr = DataManager()

FLIGHT_SEARCH_API_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"
SEARCH_API_KEY = "D4pQsEghYsjJecPPTyR-TaTOyjpJrVop"


class FlightSearch:

    def __init__(self):
        self.city_from = None
        self.flight_from = None
        self.city_to = None
        self.flight_to = None
        self.flight_price = 0

        self.year_diff = 0
        self.months_interval = 0
        self.flight_data = None

        self.search_params = {
            "fly_from": "BVA",
            "date_from": flight_details.date_from.strftime("%d/%m/%Y"),
            "date_to": flight_details.date_to.strftime("%d/%m/%Y"),
            "one_per_date": 0,
        }

        self.headers = {
            "apikey": SEARCH_API_KEY,
        }

        response = requests.get(url=FLIGHT_SEARCH_API_ENDPOINT, params=self.search_params, headers=self.headers)
        self.flight_data = response.json()["data"]

    def calculate_interval(self):
        self.year_diff = flight_details.date_to.year - flight_details.date_from.year
        self.months_interval = self.year_diff * 12 + flight_details.date_to.month - flight_details.date_from.month

        return self.months_interval

    def cheapest_flight(self):

        for dic in self.flight_data:
            self.city_from = dic["cityFrom"]
            self.flight_from = dic["flyFrom"]
            self.city_to = dic["cityTo"]
            self.flight_to = dic["flyTo"]
            self.flight_price = dic["price"]

            if float(self.flight_price) < data_mgr.lowest_price_from_sheet():
                cheapest_flight = self.flight_from
                return cheapest_flight

    def cheapest_flight_price(self):
        return self.flight_price

    def departure_location(self):

        for dic in self.flight_data:
            self.city_from = dic["cityFrom"]
            flight = dic["flyFrom"]
            self.flight_price = dic["price"]

            if float(self.flight_price) < data_mgr.lowest_price_from_sheet():
                self.flight_from = flight
        return self.flight_from
