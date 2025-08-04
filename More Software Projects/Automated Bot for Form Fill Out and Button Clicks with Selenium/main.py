from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


chrome_driver_path = "/Users/Courses and Tutorials/Courses/Python and Django/100 Days of Code The Complete Python Pro Bootcamp for 2022/[TutsNode.com] - 100 Days of Code The Complete Python Pro Bootcamp for 2022/48 Day 48 - Inter+ Selenium Webdriver Browser, Game Play Bot/chromedriver-mac-arm64/chromedriver"
chrome_driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=chrome_driver_service)

# driver.get("https://en.wikipedia.org/wiki/Main_Page")
# article_count = driver.find_element(By.LINK_TEXT, 'View source')
# # article_count.click()
#
# search = driver.find_element(By.NAME, 'search')
# search.send_keys("Python data structures and algorithms")
# search.send_keys(Keys.ENTER)

driver.get('http://secure-retreat-92358.herokuapp.com/')

first_name = driver.find_element(By.NAME, "fName")
first_name.send_keys("Amidu")

last_name = driver.find_element(By.NAME, "lName")
last_name.send_keys("Dabor")

email = driver.find_element(By.NAME, "email")
email.send_keys("daboramidu93@gmail.com")

signup_button = driver.find_element(By.XPATH, '/html/body/form/button')
signup_button.click()

input("Press enter to close the close the browser: ")



