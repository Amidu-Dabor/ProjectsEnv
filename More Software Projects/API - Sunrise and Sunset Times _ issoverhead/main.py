import requests
from datetime import datetime
import smtplib
import time

ISS_API_URL = "http://api.open-notify.org/iss-now.json"
SUNRISE_SUNSET_API_URL = "https://api.sunrise-sunset.org/json"

MY_LAT = -1.292066
MY_LONG = 36.821945

SENDER_EMAIL = "amiddabs93@gmail.com"
PASSWORD = "zgryezbwwxjwjzik"


def iss_api():
    response = requests.get(ISS_API_URL)
    response.raise_for_status()
    data = response.json()

    return data


def sunrise_sunset_api():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }
    response = requests.get(SUNRISE_SUNSET_API_URL, params=parameters)
    response.raise_for_status()
    data = response.json()

    return data


def is_iss_overhead():
    iss_data = iss_api()
    iss_latitude = float(iss_data["iss_position"]["latitude"])
    iss_longitude = float(iss_data["iss_position"]["longitude"])

    if (MY_LAT - 5 <= iss_latitude <= MY_LAT + 5) and (MY_LONG - 5 <= iss_longitude <= MY_LONG + 5):
        return


def is_night():
    sunrise_sunset_data = sunrise_sunset_api()
    sunrise = int(sunrise_sunset_data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(sunrise_sunset_data["results"]["sunset"].split("T")[1].split(":")[0])

    my_current_time_now = datetime.now().hour

    if my_current_time_now <= sunrise or my_current_time_now >= sunset:
        return True


while True:
    time.sleep(60)

    if is_iss_overhead() and is_night():

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=SENDER_EMAIL, password=PASSWORD)
            connection.sendmail(
                                from_addr=SENDER_EMAIL,
                                to_addrs="amidu.dabor@yahoo.com",
                                msg="Subject: ISS Location Update \n"
                                    "Look up! The International Space Station(ISS) is overhead."
                                )
        print(True)
    else:
        print(False)
