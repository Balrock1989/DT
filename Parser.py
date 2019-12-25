from pprint import pprint

from bs4 import BeautifulSoup
import datetime
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException
import auth


class Parser:
    start_data = ''
    end_data = ''
    url = ''
    driver = None
    exit = False

    def auth(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(auth.auth_url_ad)
        username = self.driver.find_element_by_name('login')
        password = self.driver.find_element_by_name('password')
        username.send_keys(auth.username_ad)
        password.send_keys(auth.password_ad)
        self.driver.find_element_by_id("id_sign_in").click()

    def parser(self):
        current_window = self.driver.current_window_handle
        for window in self.driver.window_handles:
            if window is not current_window:
                self.driver.switch_to.window(window)
                new_window = window
        page = BeautifulSoup(self.driver.page_source, "lxml")
        coupun_name = page.findAll("p", {"class": "h3-name"})
        full_date = page.findAll("b", text=re.compile('.*\s*(\d+.\d+.\d+)'))
        description = page.findAll("td", {"class": "last"})
        for name in coupun_name:
            print(name.text)
        for date in full_date:
            temp = str(date.text).split()
            temp2 = "".join(temp)
            date_start = re.search(r'^(\d+.\d+.\d{4})', temp2).group(1)
            date_end = re.search(r'-(\d+.\d+.\d{4})', temp2).group(1)
            print(date_start, date_end)
        for desc in description:
            test = re.sub(r'\s+', ' ', desc.text)
            print(test[1:])

        self.driver.switch_to.window(current_window)

