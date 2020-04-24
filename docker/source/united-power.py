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

if "LOG_LEVEL" in os.environ:
    level = logging.getLevelName(os.environ["LOG_LEVEL"])
else:
    level = logging.getLevelName("INFO")

logging.basicConfig(format="%(asctime)s - %(message)s", level=level)
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

    log.info("Loading webdriver for Chrome")
    log.info("Starting query of power portal")
    driver = webdriver.Chrome(options=chrome_options)

    # Load the login page, populate username/password
    log.info("Loading main website URL")
    driver.get(base_url)
    try:
        myElem = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.ID, "_com_liferay_login_web_portlet_LoginPortlet_loginSubmitBtn")
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
        log.info("Waiting for My Consumption Data link")
        myElem = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='My Consumption Data']")
            )
        )
        log.info("Selecting My Consumption Data link, this may take a long time to load (minutes)")
        driver.find_element_by_xpath("//span[text()='My Consumption Data']").click()
    except TimeoutException:
        log.error("Loading My Consumption Data took too much time!")
        return False

    # The initial data load can take a loooooooong time to load. So wait until the
    # highcharts SVG fully rendered with a title containing "Metered"
    try:
        log.info("Waiting for Chart data set to load")
        myElem = WebDriverWait(driver, 240).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Metered')]")
            )
        )
        log.info("Chart data loaded")
    except TimeoutException:
        log.error("Loading the chart data took too much time!")
        return False

    # Now on main account page with chart loaded, set timeframe to 7 days, month type calendar month
    # Change to Timeframe -> Current Month
    try:
        log.info("Waiting for timeViews elements to load")
        myElem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeViews"))
        )
        log.info('Selecting "Current Month" radio button')
        select = Select(driver.find_element_by_id("timeViews"))
        select.select_by_value("CurrentMonth")
        log.info("Changed graph view to CurrentMonth")
    except TimeoutException:
        log.error("Changing graph to Current Month timed out!")
        return False

    # Change Month from calendar to billing
    try:
        log.info('Waiting for "Billing Month" radio button to be clickable')
        myElem = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.ID,"c_billingMonth")
            )
        )
        log.info("Selecting Billing Month")
        driver.find_element_by_id("c_billingMonth").click()
        log.info("Changed month from current to billing")
    except TimeoutException:
        log.info("Error select ingbilling month radio button")
        return False

    # Click on Highcharts menu and download the formatted CVS file to /tmp
    try:
        # Click the menu
        log.info('Waiting for download menu, then selecting "Export Formatted CSV"')
        myElem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME,"highcharts-button")
            )
        )
        driver.find_element_by_class_name("highcharts-button").click()

        # With menu opened...
        myElem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,"//div[text()='Export Formatted CSV']")
            )
        )
        # TODO - verify that /tmp/export.csv does not exist
        log.info('Clicking on "Export Formatted CSV" link')
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
        log.info("CSV file has completed download")            
        return "/tmp/export.csv"
    except TimeoutException:
        log.error("Attempting to download CSV timed out!")
        return False


def max_demand(csv_file):
    """Return the date and highest demand value"""
    demand = []
    try:
        with open(csv_file) as f:
            for row in csv.DictReader(f, skipinitialspace=True):
                demand.append(row)
                if logging.getLevelName(log.getEffectiveLevel()) == "DEBUG":
                    print(row)

        demand_record = {}
        for index, row in enumerate(demand):
            if index == 0:
                # Use first row as initial demand - can be negative based on solar
                max_demand = float(row["Demand (kW)"])
                demand_record[row["Timeperiod"]] = float(row["Demand (kW)"])
            elif float(row["Demand (kW)"]) > max_demand:
                max_demand = float(row["Demand (kW)"])
                demand_record.clear()
                demand_record[row["Timeperiod"]] = float(row["Demand (kW)"])
        return demand_record
    except KeyError:
        # Expected 'Demand (kW)', let's try again
        log.error(f"Expected 'Demand (kW)', may have received wrong file")
        log.info(f"Total contents of bad CSV file:\n {demand}\n\n")
        return False


if __name__ == "__main__":
    # Get the demand charge CSV from United Power

    csv_file = get_demand_charge()
    if csv_file:
        demand_kw = max_demand(csv_file)
        if demand_kw:
            print(f"Demand record: {demand_kw}")
        else:
            log.error("Could not read CSV properly")
    else:
        log.error("Could not scrape website")