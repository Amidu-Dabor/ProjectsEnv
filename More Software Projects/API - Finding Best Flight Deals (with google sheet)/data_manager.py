import requests

# Sheety API details
USER_ID = "ba55e218687f1817e23838d692899c6f"
PROJECT_NAME = "copyOfFlightDeals"
SHEET_NAME = "prices"
SHEETY_API_URL = f"https://api.sheety.co/{USER_ID}/{PROJECT_NAME}/{SHEET_NAME}"


class DataManager:

    def __init__(self):
        self.sheet_prices = []
        self.sheet_lowest_price = 0

        self.response = requests.get(url=SHEETY_API_URL)
        self.dep_locations_and_prices = self.response.json()["prices"]

    def lowest_price_from_sheet(self):
        for dic in self.dep_locations_and_prices:
            self.sheet_prices.append(dic["lowestPrice"])
            self.sheet_lowest_price = min(self.sheet_prices)
        return float(self.sheet_lowest_price)
