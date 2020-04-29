# Class to create, query, and extract data from United Power's web site
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class UnitedPowerUsage:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password

        # Set last billing year and current billing month usage
        # Values will be all columns pulled from CSV export file
        self.billing_year_usage = {}
        self.current_month_usage = {}

    
    def __create_session(self):
        """Establish selenium session"""
        logger.debug(f"Creating a new Selenium session")

        # Instantiate a chrome options object so you can set the size and headless preference
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
        logger.info("Loading webdriver for Chrome")
        return webdriver.Chrome(options=chrome_options)


    def __login(self, driver):
        """Log into web site with credentials"""

        # Load the login page, populate username/password
        logger.info("Loading main website URL")
        driver.get(self.url)
        try:
            myElem = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.ID, "_com_liferay_login_web_portlet_LoginPortlet_loginSubmitBtn")
                )
            )
            driver.find_element_by_id(
                "_com_liferay_login_web_portlet_LoginPortlet_login"
            ).send_keys(self.username)
            driver.find_element_by_id(
                "_com_liferay_login_web_portlet_LoginPortlet_password"
            ).send_keys(self.password)
            driver.find_element_by_id(
                "_com_liferay_login_web_portlet_LoginPortlet_loginSubmitBtn"
            ).click()
            logger.info("Submitted login credentials, goto main account page")
            return True
        except TimeoutException:
            logger.error("Loading main authenticated page too much time!")
            return False



    def load_billing_year(self):
        """Create selenium session to website, download last years usage data by billing date"""
        driver = self.__create_session()

        
