import requests
import os
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
article_title = None
article_desc = None

# Stock
stock_price_api = 'https://www.alphavantage.co/query'
# News
news_piece_api = 'https://newsapi.org/v2/everything'

# proxy_client = TwilioHttpClient(proxy={'http': os.environ['http_proxy'], 'https': os.environ['https_proxy']})
# Twilio account details
account_sid = "AC939811610f03e1e597fcdfa04f53f4be"
auth_token = "084f9331f5bf75bcce43981d4b7bbf89"

# STOCK
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": "HZWKWQ95J8I6NA67",
}

stock_response = requests.get(stock_price_api, params=stock_params)
data = stock_response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]

yesterday_closing_price = float(data_list[0]["4. close"])
day_before_closing_price = float(data_list[1]["4. close"])

# Calculate the positive difference using absolute function
difference = yesterday_closing_price - day_before_closing_price
difference_in_percentage = round((difference / yesterday_closing_price) * 100)

# NEWS
news_piece_params = {
            "q": COMPANY_NAME,
            "apiKey": "93b796b076c247f7a90408693415e797",
        }

news_response = requests.get(news_piece_api, params=news_piece_params)
articles = news_response.json()["articles"][:3]
articles_details = [(article["title"], article["description"]) for article in articles]

for detail in articles_details:
    article_title = detail[0]
    article_desc = detail[1]

    client = Client(account_sid, auth_token)

    if abs(difference_in_percentage) < 0:
        message = client.messages.create(
            body=f"{STOCK}: 🔻{difference_in_percentage}% \n"
                f"Headline: {article_title} \n"
                f"Brief: {article_desc}",
            from_='+16185912908',
            to='+254795455796',
        )
    elif abs(difference_in_percentage) > 0:
        message = client.messages.create(
            body=f"{STOCK}: 🔺{difference_in_percentage}% \n"
                 f"Headline: {article_title} \n"
                 f"Brief: {article_desc}",
            from_='+16185912908',
            to='+254795455796',
        )

