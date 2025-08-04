import smtplib
from datetime import datetime
import random


current_day = datetime.now().strftime("%A")
# current_day = now.day

with open("quotes.txt", mode="r") as file:
    list_of_quotes = file.readlines()
    quote = random.choice(list_of_quotes)


my_email = "amiddabs93@gmail.com"
password = "zgryezbwwxjwjzik"

with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=my_email, password=password)
    connection.sendmail(from_addr=my_email,
                        to_addrs="amidu.dabor@yahoo.com",
                        msg=f"Subject: {current_day}'s Motivational Quote "
                            f"\n\n{quote}"
                        )




