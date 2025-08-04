from flight_search import FlightSearch
from notification_manager import NotificationManager


f_search = FlightSearch()
notification_mgr = NotificationManager()

if f_search.cheapest_flight() and f_search.cheapest_flight_price():
    notification_mgr.send_sms()


