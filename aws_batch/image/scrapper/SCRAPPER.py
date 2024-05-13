import time
from abc import ABC, abstractmethod
from selenium import webdriver as detected_webdriver
import undetected_chromedriver as undetected_webdriver
import chromedriver_autoinstaller
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import logging
import os
import traceback


#For chrome drive in AWS Lambda
#https://github.com/umihico/docker-selenium-lambda/blob/main/Dockerfile
#https://github.com/diegoparrilla/headless-chrome-aws-lambda-layer/tree/main
@dataclass
class STORESCRAPPER(ABC):
    params: dict
    drive: any = field(init=False)
    wait: any = field(init=False)
    ROOT_DIR: str
    store_name: str = field(init=False)
    output_filepath: str = field(init=False)

    def start_driver(self, display):
        """
        The function `start_driver` starts a Chrome driver with specified options and returns the webdriver
        object.
        
        :param display: The `display` parameter is a boolean value that determines whether the Chrome
        browser should be displayed or run in headless mode. If `display` is `True`, the browser will be
        displayed, otherwise it will run in headless mode
        :return: The code is returning an instance of the `webdriver.Chrome` class.
        """
        try:
            logging.info('Starting chrome driver...')
            chrome_options = Options()
            chrome_options.page_load_strategy = "eager"
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('enable-automation')
            if not display:
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            driver_path = chromedriver_autoinstaller.install()
            time.sleep(60)
            if self.store_name == 'Metro':
                return undetected_webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)
            else:
                return detected_webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)
        except Exception as e:
            print(traceback.format_exc())
            raise Exception(e)

    def initialize_web_drive(self, display=False):
        """
        The function initializes a web driver, sets a wait time, and defines an output file path.
        
        :param display: The `display` parameter is a boolean value that determines whether or not the web
        driver should be displayed on the screen while running. If `display` is set to `True`, the web
        driver will be visible on the screen. If `display` is set to `False`, the web driver will, defaults
        to False (optional)
        """
        self.drive = self.start_driver(display)
        self.wait = WebDriverWait(self.drive, 90)
        self.output_filepath = os.path.join(self.ROOT_DIR, f"{self.store_name}_{datetime.now(timezone(timedelta(hours=-5))).strftime('%Y-%m-%d')}_{self.event_num}.csv")

    def reinitialize_web_drive(self, url, sleep_time=15):
        print('Re initializing the web driver...')
        self.initialize_web_drive()
        time.sleep(sleep_time)
        self.drive.get(url)
        time.sleep(sleep_time)

    @abstractmethod
    def scrap_main(self):
        pass
