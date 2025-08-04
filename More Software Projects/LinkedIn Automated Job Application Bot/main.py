from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time


ACCOUNT_EMAIL = "YOUR LOGIN EMAIL"
ACCOUNT_PASSWORD = "YOUR LOGIN PASSWORD"
PHONE = "YOUR PHONE NUMBER"

chrome_driver_path = "/Users/Courses and Tutorials/Courses/Python and Django/100 Days of Code The Complete Python Pro Bootcamp for 2022/[TutsNode.com] - 100 Days of Code The Complete Python Pro Bootcamp for 2022/48 Day 48 - Inter+ Selenium Webdriver Browser, Game Play Bot/chromedriver-mac-arm64/chromedriver"
chrome_driver_service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=chrome_driver_service)
driver.get('https://www.linkedin.com/jobs/search/?currentJobId=3708167299&distance=25&f_AL=true&f_E=1%2C2%2C3%2C4&geoId=101339379&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true')

time.sleep(2)
sign_in_button = driver.find_element(By.LINK_TEXT, "Sign in")
sign_in_button.click()

time.sleep(5)
email_field = driver.find_element(By.ID, "username")
email_field.send_keys(ACCOUNT_EMAIL)
password_field = driver.find_element(By.ID, "password")
password_field.send_keys(ACCOUNT_PASSWORD)
password_field.send_keys(Keys.ENTER)

time.sleep(5)

all_listings = driver.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")

for listing in all_listings:
    print("called")
    listing.click()
    time.sleep(2)

    # Try to locate the apply button, if can't locate then skip the job.
    try:
        apply_button = driver.find_element(By.CSS_SELECTOR, ".jobs-s-apply button")
        apply_button.click()
        time.sleep(5)

        # If phone field is empty, then fill your phone number.
        phone = driver.find_element(By.CLASS_NAME, "fb-single-line-text__input")
        if phone.text == "":
            phone.send_keys(PHONE)

        submit_button = driver.find_element(By.CSS_SELECTOR, "footer button")

        # If the submit_button is a "Next" button, then this is a multi-step application, so skip.
        if submit_button.get_attribute("data-control-name") == "continue_unify":
            close_button = driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss")
            close_button.click()
            time.sleep(2)
            discard_button = driver.find_elements(By.CLASS_NAME, "artdeco-modal__confirm-dialog-btn")[1]
            discard_button.click()
            print("Complex application, skipped.")
            continue
        else:
            submit_button.click()

        # Once application completed, close the pop-up window.
        time.sleep(2)
        close_button = driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss")
        close_button.click()

    # If already applied to job or job is no longer accepting applications, then skip.
    except NoSuchElementException:
        print("No application button, skipped.")
        continue

time.sleep(5)
driver.quit()

