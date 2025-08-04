import pandas as pd
import os
import random
import smtplib
from datetime import datetime


SENDER_EMAIL = "amiddabs93@gmail.com"
PASSWORD = "zgryezbwwxjwjzik"

today = datetime.now()
birthday_tuple = (today.month, today.day)

data = pd.read_csv("birthdays.csv")
birthdays_dic = {(row.month, row.day): row for (index, row) in data.iterrows()}

if birthday_tuple in birthdays_dic:

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=SENDER_EMAIL, password=PASSWORD)

        for birthday, recipient_info in birthdays_dic.items():
            if birthday == birthday_tuple:
                recipient_name = recipient_info["name"]
                recipient_email = recipient_info["email"]

                letter = random.choice(os.listdir("letter_templates"))
                with open(f"letter_templates/{letter}") as file:
                    contents = file.read()
                    letter_contents = contents.replace("[NAME]", recipient_name)

                connection.sendmail(
                                    from_addr=SENDER_EMAIL,
                                    to_addrs=recipient_email,
                                    msg=f"Subject: Birthday Wishes \n\n"
                                        f"{letter_contents}"
                                    )




