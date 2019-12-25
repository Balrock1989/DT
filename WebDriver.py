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


class AddBanner:
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
        self.driver.get(auth.auth_url_dt)
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')
        username.send_keys(auth.username_dt)
        password.send_keys(auth.password_dt)
        self.driver.find_element_by_class_name("submit").click()

    def add_banner(self, gui):
        try:
            wait = WebDriverWait(self.driver, 5, poll_frequency=3, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='_____']")))
            links = list(filter(lambda x: len(x.get_attribute('href')) > 150, links))
            links = set(map(lambda x: x.get_attribute('href'), links))
            links = list(links)
            links = sorted(links, key=lambda x: re.search(r'_____(\d+).', x).group(1))
            dir_name = self.driver.find_elements_by_css_selector('tr th')[0]
            dir_name = re.search(r'Хостинг файлов: (.*)', dir_name.text).group(1)
            gui.command_window.append(
                f'В работе "{len(links)}" баннер(ов) из папки: {dir_name}')
            gui.command_window.append(
                f'Дата начала акции:{self.start_data}, Дата окончания акции:{self.end_data}, url: {self.url}')
            if not self.start_data:
                now = datetime.datetime.now()
                self.start_data = now.strftime("%d.%m.%Y")
            for link in links:
                if self.exit:
                    return
                self.driver.get(link)
                size = self.driver.find_element_by_css_selector("input[id*='geTitle']").get_attribute('value')
                width = re.search(r'(\d+)__\d\d', size).group(1)
                height = re.search(r'__(\d+)x', size).group(1)
                width_field = self.driver.find_element_by_name('width')
                height_field = self.driver.find_element_by_name('height')
                start_data_field = self.driver.find_element_by_css_selector(
                    "input[name='graphicalElementTransport.startDate']")
                end_data_field = self.driver.find_element_by_css_selector(
                    "input[name='graphicalElementTransport.endDate']")
                url_field = self.driver.find_element_by_css_selector(
                    "textarea[name='graphicalElementTransport.description']")
                width_field.clear()
                height_field.clear()
                width_field.send_keys(width)
                height_field.send_keys(height)
                self.driver.find_element_by_class_name('noDecoration').click()
                start_data_field.send_keys(self.start_data)
                end_data_field.send_keys(self.end_data)
                url_field.send_keys(self.url)
                sleep(1)
                self.driver.find_elements_by_css_selector("input[value='Предварительный']")[1].click()
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[value='Сохранить']"))).click()
                gui.command_window.append(f'файл {size} успешно загружен')
            gui.command_window.append('#' * 60)
            gui.command_window.append('#' * 60)
            gui.command_window.append('С первой папкой закончил, жду следующую')
        except WebDriverException as exc:
            print(f'Произошла ошибка {exc}')
            if 'chrome not reachable' in exc.msg:
                gui.command_window.append('Браузер закрылся')
                return
        except AttributeError as exc:
            gui.command_window.append('Необходимо перейти в браузере в папку с баннерами')



