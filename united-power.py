#!/usr/bin/env python3

import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# instantiate a chrome options object so you can set the size and headless preference
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": "/tmp",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})
chrome_driver = "~/bin/chromedriver.exe"

username = os.environ["UNITED_POWER_USERNAME"]
password = os.environ["UNITED_POWER_PASSWORD"]

# changes to power portal once I get the PIN
base_url = "https://consumer.sgsportal.com/web/unitedpower/login/"
delay = 3 # seconds

# driver = webdriver.Firefox()
driver = webdriver.Chrome(options=chrome_options)
# Load the login page, populate username/password
driver.get(base_url)
try:
    myElem = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, '_com_liferay_login_web_portlet_LoginPortlet_login')))
    driver.find_element_by_id("_com_liferay_login_web_portlet_LoginPortlet_login").send_keys(username)
    driver.find_element_by_id("_com_liferay_login_web_portlet_LoginPortlet_password").send_keys(password)
    driver.find_element_by_id("_com_liferay_login_web_portlet_LoginPortlet_loginSubmitBtn").click()
    print("Submitted login credentials, goto main account page")
except TimeoutException:
    print("Loading took too much time!")
    sys.exit(1)

# From main page, click "My Consumption Data"
try:
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='My Consumption Data']")))
    driver.find_element_by_xpath("//span[text()='My Consumption Data']").click()
except TimeoutException:
    print("Loading took too much time!")
    sys.exit(1)

# The initial data load can take a loooooooong time to load. So wait until the
# chart title loads
try:
    myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "chartContainer")))
    print("Chart data loaded")
except TimeoutException:
    print("Loading took too much time!")
    sys.exit(1)

# Now on main account page with chart loaded, set timeframe to 7 days, month type calendar month
# Change to Timeframe -> Current Month
try:
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "timeViews")))
    select = Select(driver.find_element_by_id('timeViews'))
    select.select_by_value("CurrentMonth")
    print("Changed graph view to CurrentMonth")
except TimeoutException:
    print("Loading took too much time!")

# Change Month from calendar to billing
try:
    driver.find_element_by_css_selector("input[type='radio'][value='billing']").click()
    print("Changed month from current to billing")
except TimeoutException:
    print("Loading took too much time!")

# Click on Highcharts menu and download the formatted CVS file to /tmp

# rm /tmp/export*
try:
    # Click the menu
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-button")))
    driver.find_element_by_class_name('highcharts-button').click()
    # With menu opened...
    driver.find_element_by_xpath("//div[text()='Export Formatted CSV']").click()
    print("formatted CSV downloaded")
except TimeoutException:
    print("Loading took too much time!")
