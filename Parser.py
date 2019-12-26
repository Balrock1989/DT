from pprint import pprint

from bs4 import BeautifulSoup
import datetime
import re
from time import sleep

from collections import OrderedDict
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
    data = []

    def auth(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=options)

        self.driver.get(auth.auth_url_ad)
        username_ad = self.driver.find_element_by_name('login').send_keys(auth.username_ad)
        password_ad = self.driver.find_element_by_name('password').send_keys(auth.password_ad)
        self.driver.find_element_by_id("id_sign_in").click()

    def parser(self, gui):
        try:
            current_window = self.driver.current_window_handle
            for window in self.driver.window_handles:
                if window is not current_window:
                    self.driver.switch_to.window(window)
                    new_window = window
            page = BeautifulSoup(self.driver.page_source, "lxml")
            actions = page.findAll('div', class_="coupon")
            for act in actions:
                action = OrderedDict()
                action["Имя партнера"] = act.findAll("b", text=True)[1].text.strip()
                action["Название акции"] = act.find("p", {"class": "h3-name"}).text.strip()
                full_date = act.find("b", text=re.compile('.*\s*(\d+.\d+.\d+)'))
                temp = "".join(str(full_date.text).split())
                action["Дата начала"] = re.search(r'^(\d+.\d+.\d{4})', temp).group(1)
                action["Дата окончания"] = re.search(r'-(\d+.\d+.\d{4})', temp).group(1)
                action["Тип купона"] = re.sub(r'\s+', ' ', act.div.h3.text).strip()
                action["Условия акции"] = act.findAll("p", text=True)[1].text.strip() \
                    if len(act.findAll("p", text=True)) > 1 else ""
                self.data.append(action)
            pprint(self.data)
            self.driver.switch_to.window(current_window)
        except WebDriverException as exc:
            print(f'Произошла ошибка {exc}')
        except AttributeError as exc:
            print(f'Произошла ошибка {exc}')




