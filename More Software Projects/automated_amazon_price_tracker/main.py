import requests
import lxml
from bs4 import BeautifulSoup


product_url = "https://www.amazon.com/Instant-Pot-Ultra-Programmable-Sterilizer/dp/B06Y1MP2PY/ref=sr_1_7?crid=KWSSND4J6X9Y&keywords=instant%2Bpot%2Bduo%2Bevo%2Bplus&qid=1694722227&sprefix=instant%2Bpot%2Bdou%2Caps%2C389&sr=8-7&th=1"
header = {
    "Accept-Language": "en-GB,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
}
response = requests.get(product_url, headers=header)
contents = response.content

soup = BeautifulSoup(contents, "lxml")
price = soup.find(class_="a-price-whole")
product_price = f"Product Price: ${float(price.getText())}"

print(product_price)

