import datetime
import os
import re
from collections import OrderedDict
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException
import auth


class WebDriver:
    start_data = ''
    end_data = ''
    url = ''
    driver = None
    exit = False
    dt_window = None
    ad_window = None
    actions_data = []
    name_index = 1

    def auth(self, gui):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(auth.auth_url_dt)
        self.dt_window = self.driver.current_window_handle
        self.driver.find_element_by_id('username').send_keys(auth.username_dt)
        self.driver.find_element_by_id('password').send_keys(auth.password_dt)
        self.driver.find_element_by_class_name("submit").click()
        self.driver.execute_script("window.open('');")
        self.ad_window = self.driver.window_handles[1]
        self.driver.switch_to_window(self.ad_window)
        self.driver.get(auth.auth_url_ad)
        self.driver.find_element_by_name('login').send_keys(auth.username_ad)
        self.driver.find_element_by_name('password').send_keys(auth.password_ad)
        self.driver.find_element_by_id("id_sign_in").click()

    def add_banner(self, gui):
        try:
            self.driver.switch_to_window(self.dt_window)
            wait = WebDriverWait(self.driver, 5, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='_____']")))
            links = list(filter(lambda x: len(x.get_attribute('href')) > 150, links))
            links = set(map(lambda x: x.get_attribute('href'), links))
            links = list(links)
            links = sorted(links, key=lambda x: re.search(r'_____(\d+).', x).group(1))
            dir_name = self.driver.find_elements_by_css_selector('tr th')[0]
            dir_name = re.search(r'Хостинг файлов: (.*)', dir_name.text).group(1)
            gui.chat.queue.put(gui.command_window.append(f'В работе "{len(links)}" баннер(ов) из папки: {dir_name}'))
            gui.chat.queue.put(gui.command_window.append(f'Дата начала акции:{self.start_data}, Дата окончания акции:'
                                                         f'{self.end_data}, url: {self.url}'))
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
                gui.chat.queue.put(gui.command_window.append(f'файл {size} успешно загружен'))
            gui.chat.queue.put(gui.command_window.append('#' * 60))
            gui.chat.queue.put(gui.command_window.append('#' * 60))
            gui.chat.queue.put(gui.command_window.append('С первой папкой закончил, жду следующую'))
        except WebDriverException as exc:
            print(f'Произошла ошибка {exc}')
            if 'chrome not reachable' in exc.msg:
                gui.chat.queue.put(gui.command_window.append(f'Ошибка браузера {exc}, {exc.msg}'))
                return
        except AttributeError as exc:
            gui.chat.queue.put(gui.command_window.append('Необходимо открыть папку с баннерами в браузере'))

    def parser(self, gui):
        self.driver.switch_to_window(self.ad_window)
        for window in self.driver.window_handles:
            if window != self.dt_window and window != self.ad_window:
                self.driver.switch_to.window(window)
        page = BeautifulSoup(self.driver.page_source, "lxml")
        actions = page.findAll('div', class_="coupon")
        gui.chat.queue.put(gui.command_window.append(f"Всего будет обработано акций {len(actions)}"))
        for act in actions:
            action = OrderedDict()
            action["Имя партнера"] = act.findAll("b", text=True)[1].text.strip()
            action["Название акции"] = act.find("p", {"class": "h3-name"}).text.strip()
            full_date = act.find("b", text=re.compile('.*\s*(\d+.\d+.\d+)'))
            temp = "".join(str(full_date.text).split())
            action["Дата начала"] = re.search(r'^(\d+.\d+.\d{4})', temp).group(1)
            action["Дата окончания"] = re.search(r'-(\d+.\d+.\d{4})', temp).group(1)
            action["Тип купона"] = re.sub(r'\s+', ' ', act.findAll("td", text=True)[4].text).strip()
            action["Условия акции"] = act.findAll("p", text=True)[1].text.strip() if \
                len(act.findAll("p", text=True)) > 1 else ""
            self.actions_data.append(action)
        info = ""
        for n, a in enumerate(self.actions_data, 1):
            gui.chat.queue.put(gui.command_window.append(info))
            info = f"---№{n}\n"
            for key, value in a.items():
                info += " ".join([key, ':  ', value]) + "\n"
        gui.chat.queue.put(gui.command_window.append(info))
        if self.driver.current_window_handle != self.ad_window and \
                self.driver.current_window_handle != self.dt_window:
            self.driver.close()
        self.driver.switch_to.window(self.ad_window)

    def add_actions(self, gui):
        try:
            for action in self.actions_data:
                self.driver.switch_to_window(self.dt_window)
                url = self.driver.current_url
                id = re.search(r'Id=(\d+)', url).group(1)
                self.driver.switch_to_frame("ifrm")
                header = self.driver.find_element_by_name("title")
                vaucher_type = Select(self.driver.find_element_by_id("voucherTypeId"))
                form = self.driver.find_element_by_css_selector('form[id="createVoucherForm"]')
                checkbox = self.driver.find_element_by_id("isPercentage")
                description = self.driver.find_element_by_id("description")
                short_description = self.driver.find_element_by_name("shortDescription")
                discount_amount = self.driver.find_element_by_id("discountAmount")
                valid_from = self.driver.find_element_by_id("id_startDate")
                valid_to = self.driver.find_element_by_id("id_endDate")
                start_date = self.driver.find_element_by_id("id_publishStartDate")
                end_date = self.driver.find_element_by_id("id_publishEndDate")
                code = self.driver.find_element_by_id("code")
                landing_url = self.driver.find_element_by_id("landingUrl")
                header.send_keys(action["Название акции"])
                valid_from.clear()
                valid_from.send_keys(action["Дата начала"])
                valid_to.clear()
                valid_to.send_keys(action["Дата окончания"])
                start_date.clear()
                start_date.send_keys(action["Дата начала"])
                end_date.clear()
                end_date.send_keys(action["Дата окончания"])
                short_description.send_keys(action["Название акции"])
                if action["Условия акции"]:
                    description.send_keys(action["Условия акции"])
                else:
                    description.send_keys(action["Название акции"])
                landing_url.send_keys(gui.url.toPlainText())
                if "кидка" or "упон" in action["Тип купона"]:
                    vaucher_type.select_by_value("2") if "кидка" in action["Тип купона"] \
                        else vaucher_type.select_by_value("1")
                    code.send_keys("Не требуется")
                    if "%" in action["Название акции"]:
                        checkbox.click()
                        percent = self.get_percent(action["Название акции"])
                        discount_amount.send_keys(percent)
                    elif "%" in action["Условия акции"]:
                        checkbox.click()
                        percent = self.get_percent(action["Условия акции"])
                        discount_amount.send_keys(percent)
                    else:
                        discount_amount.send_keys('0')
                if "одарок" in action["Тип купона"]:
                    vaucher_type.select_by_value("3")
                    code.send_keys("Не требуется")
                if "оставка" in action["Тип купона"]:
                    vaucher_type.select_by_value("4")
                    code.send_keys("Не требуется")
                form.submit()
                self.driver.switch_to_default_content()
                sleep(1)
                self.driver.find_element_by_id("VOUCHERS_MERCHANT_AD_MANAGEMENT_VOUCHERS_CREATE").click()
                self.driver.get("https://login.tradedoubler.com/pan/mCreateVouchers.action?programId=" + id)
            self.actions_data.clear()
            gui.chat.queue.put(gui.command_window.append("Акции успешно добавлены"))

        except WebDriverException as exc:
            print(f'Произошла ошибка {exc}')
            gui.chat.queue.put(gui.command_window.append(f'Ошибка браузера {exc}, {exc.msg}'))
        except AttributeError as exc:
            gui.chat.queue.put(gui.command_window.append(f'Данные об акциях очищены, нужно загрузить снова'))
            self.actions_data.clear()

    def get_percent(self, action):
        try:
            percent = re.search(r'(\d+)%', action).group(1)
        except AttributeError:
            percent = re.search(r'%(\d+)', action).group(1)
        return percent

    def download_banners(self, gui):
        try:
            for window in self.driver.window_handles:
                if window != self.dt_window and window != self.ad_window:
                    self.driver.switch_to.window(window)
            wait = WebDriverWait(self.driver, 5, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class='banner_view']")))
            links = set(map(lambda x: x.get_attribute('href'), links))
            links = list(links)
            if links:
                home_path = os.getenv('HOMEPATH')
                result = os.path.join("C:\\", home_path, "Desktop", "result")
                result = os.path.normpath(result)
                if not os.path.exists(result):
                    os.mkdir(result)
                gui.chat.queue.put(gui.command_window.append(f'Всего будет скачано {len(links)} баннеров'))
                gui.chat.queue.put(gui.command_window.append(f'Результаты здесь: {os.path.abspath(result)}'))
                for link in links:
                    format = re.search(r'(\w+)$', link).group(1)
                    name = str(self.name_index) + "." + format
                    self.name_index += 1
                    path = os.path.join(result, name)
                    p = requests.get(link)
                    out = open(path, "wb")
                    out.write(p.content)
                    out.close()
                    gui.chat.queue.put(gui.command_window.append(f'{name} успешно скачан\n'))
                self.driver.switch_to_window(self.ad_window)
                gui.chat.queue.put(gui.command_window.append(f'Загрузка успешно завершена'))
            else:
                gui.chat.queue.put(gui.command_window.append('Нужно зайти на страницу с баннерами'))
        except WebDriverException as exc:
            print(f'Произошла ошибка {exc.msg}')
            gui.chat.queue.put(gui.command_window.append('Нужно зайти на страницу с баннерами'))
            if 'chrome not reachable' in exc.msg:
                gui.chat.queue.put(gui.command_window.append(f'Ошибка браузера {exc}, {exc.msg}'))
                return
        except AttributeError as exc:
            gui.chat.queue.put(gui.command_window.append('Нужно зайти на страницу с баннерами'))
