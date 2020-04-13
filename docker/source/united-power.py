#!/usr/bin/env python3

import os
import sys
import time
import datetime
import csv
import logging
from os import listdir
from os.path import isfile, join
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

username = os.environ["UNITED_POWER_USERNAME"]
password = os.environ["UNITED_POWER_PASSWORD"]
base_url = "https://consumer.sgsportal.com/web/unitedpower/login/"
# Default delay (seconds)
delay = 3


def get_demand_charge():
    """Use selenium and chrome to log in to portal and get the current
        months demand charge via CSV file
    """

    # instantiate a chrome options object so you can set the size and headless preference
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": "/tmp",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    log.info("Starting query of power portal")
    # driver = webdriver.Firefox()
    driver = webdriver.Chrome(options=chrome_options)
    # Load the login page, populate username/password
    log.info("getting main website URL")
    driver.get(base_url)
    try:
        myElem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.ID, "_com_liferay_login_web_portlet_LoginPortlet_login")
            )
        )
        driver.find_element_by_id(
            "_com_liferay_login_web_portlet_LoginPortlet_login"
        ).send_keys(username)
        driver.find_element_by_id(
            "_com_liferay_login_web_portlet_LoginPortlet_password"
        ).send_keys(password)
        driver.find_element_by_id(
            "_com_liferay_login_web_portlet_LoginPortlet_loginSubmitBtn"
        ).click()
        log.info("Submitted login credentials, goto main account page")
    except TimeoutException:
        log.error("Loading main authenticated page too much time!")
        return False

    # From main page, click "My Consumption Data"
    try:
        myElem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[text()='My Consumption Data']")
            )
        )
        driver.find_element_by_xpath("//span[text()='My Consumption Data']").click()
    except TimeoutException:
        log.error("Loading My Consumption Data took too much time!")
        return False

    # The initial data load can take a loooooooong time to load. So wait until the
    # highcharts SVG fully rendered with a title containing "Metered"
    try:
        myElem = WebDriverWait(driver, 240).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Metered')]")
            )
        )
        log.info("Chart data loaded")
    except TimeoutException:
        log.error("Loading the chart data took too much time!")
        return False

    # Appears to be a timing issue when the dataset has fully loaded and when the demand CSV is available
    # Adding wait to let highcharts dataset settle before interacting with buttons
    log.info("Waiting 2 seconds before interacting with dataset")
    time.sleep(2)
    log.info("Nap over, change to curent month->billing month->download formatted CSV")

    # Now on main account page with chart loaded, set timeframe to 7 days, month type calendar month
    # Change to Timeframe -> Current Month
    try:
        myElem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeViews"))
        )
        select = Select(driver.find_element_by_id("timeViews"))
        select.select_by_value("CurrentMonth")
        log.info("Changed graph view to CurrentMonth")
    except TimeoutException:
        log.error("Changing graph to CurrentMonth timed out!")
        return False

    # Change Month from calendar to billing
    try:
        myElem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='radio'][value='billing']")
            )
        )
        driver.find_element_by_id("c_billingMonth").click()
        # driver.find_element_by_css_selector(
        #     "input[type='radio'][value='billing']"
        # ).click()
        log.info("Changed month from current to billing")
    except TimeoutException:
        log.info("Did not select billing month radio button in time")
        return False

    # Still getting random CSV for calendar month, what a bit for starting download
    log.info("Waiting 2 seconds before selecting dropdown menu")
    time.sleep(2)
    log.info("Nap over, click on dropdown for Exported Formatted CSV")

    # Click on Highcharts menu and download the formatted CVS file to /tmp
    try:
        # Click the menu
        myElem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "highcharts-button"))
        )
        driver.find_element_by_class_name("highcharts-button").click()
        # With menu opened...
        driver.find_element_by_xpath("//div[text()='Export Formatted CSV']").click()
        log.info("formatted CSV download started")

        wait_until = datetime.datetime.now() + timedelta(seconds=30)
        break_loop = False
        while not break_loop:
            if os.path.isfile("/tmp/export.csv"):
                break
            elif wait_until < datetime.datetime.now():
                break_loop = True
            time.sleep(2)
        if break_loop:
            log.error("/tmp/export.csv file not downloaded")
            return False
        # File download completed
        return "/tmp/export.csv"
    except TimeoutException:
        log.error("Attempting to download CSV timed out!")
        return False


def max_demand(csv_file):
    """Return the date and highest demand value"""
    demand = []
    with open(csv_file) as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            demand.append(row)
        log.info(f"Total contents of CSV file: {demand}")

    max_demand = 0.0
    demand_record = {}
    for row in demand:
        if float(row["Demand (kW)"]) > max_demand:
            max_demand = float(row["Demand (kW)"])
            demand_record.clear()
            demand_record[row["Timeperiod"]] = float(row["Demand (kW)"])
    return demand_record


if __name__ == "__main__":
    # Get the demand charge CSV from United Power
    csv_file = get_demand_charge()
    demand_kw = max_demand(csv_file)

    print(f"Maximum demand details: {demand_kw}")
