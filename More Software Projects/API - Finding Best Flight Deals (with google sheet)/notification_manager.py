from twilio.rest import Client
from flight_search import FlightSearch
from flight_data import FlightData


f_search = FlightSearch()
flight_details = FlightData()


class NotificationManager:

    def __init__(self):

        self.account_sid = "AC939811610f03e1e597fcdfa04f53f4be"
        self.auth_token = "084f9331f5bf75bcce43981d4b7bbf89"
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self):
        self.client.messages.create(
            body=f"Best flight! Only pay ${f_search.flight_price} to fly from\n"
                 f"{f_search.city_from}-{f_search.flight_from} to {f_search.city_to}-{f_search.flight_to},\n"
                 f"from {flight_details.date_from} to {flight_details.date_to}.",
            from_='+16185912908',
            to='+254795455796'
        )



