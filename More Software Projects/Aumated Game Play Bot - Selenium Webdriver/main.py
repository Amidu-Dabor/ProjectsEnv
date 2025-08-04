import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


chrome_driver_path = "/Users/Courses and Tutorials/Courses/Python and Django/100 Days of Code The Complete Python Pro Bootcamp for 2022/[TutsNode.com] - 100 Days of Code The Complete Python Pro Bootcamp for 2022/48 Day 48 - Inter+ Selenium Webdriver Browser, Game Play Bot/chromedriver-mac-arm64/chromedriver"
chrome_driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=chrome_driver_service)

driver.get('https://orteil.dashnet.org/experiments/cookie/')

# Get cookies to make
cookie = driver.find_element(By.ID, 'cookie')

items = driver.find_elements(By.CSS_SELECTOR, "#store div")
item_ids = [item.get_attribute("id") for item in items]

timeout = time.time() + 5
threshold = time.time() + (5 * 60)

while True:
    cookie.click()

    # Every 5 seconds
    if time.time() > timeout:
        # Get all upgrade <b> tags
        all_prices = driver.find_elements(By.CSS_SELECTOR, "#store b")
        item_prices = []

        # Convert <b> text into an integer price.
        for price in all_prices:
            element_text = price.text
            if element_text != "":
                cost = int(element_text.split("-")[1].strip().replace(",", ""))
                item_prices.append(cost)

        # Create dictionary of store items and prices
        cookie_upgrades = {}
        for n in range(len(item_prices)):
            cookie_upgrades[item_prices[n]] = item_ids[n]

        # Get current cookie count
        money_element = driver.find_element(By.ID, "money").text
        if "," in money_element:
            money_element = money_element.replace(",", "")
        cookie_count = int(money_element)

        # Find upgrades that we can currently afford
        affordable_upgrades = {}
        for cost, id_ in cookie_upgrades.items():
            if cookie_count > cost:
                affordable_upgrades[cost] = id_

        # Purchase the most expensive affordable upgrade
        highest_price_affordable_upgrade = max(affordable_upgrades)
        print(highest_price_affordable_upgrade)
        to_purchase_id = affordable_upgrades[highest_price_affordable_upgrade]

        driver.find_element(By.ID, to_purchase_id).click()

        # Add another 5 seconds until the next check
        timeout = time.time() + 5

    if time.time() > threshold:
        cookies_per_second = driver.find_element(By.ID, 'cps')
        print(cookies_per_second.text)

        break


# An input to prevent the selenium webdriver browser from closing automatically
input("Press enter to close the close the browser: ")


