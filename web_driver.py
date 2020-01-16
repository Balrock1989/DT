import datetime
import os
import re
from calendar import monthrange
from collections import OrderedDict
from time import sleep
import requests
from PyQt5 import QtCore, QtGui
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
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
    month_name = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
                  "05": "мая", "06": "июн", "07": "июл", "08": "авг",
                  "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }
    parser_handlers = ['parser_sephora']

    def auth(self, gui):
        """Запуск браузера и авторизация на сайтах"""
        if self.driver is None:
            options = Options()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(auth.auth_url_dt)
            self.dt_window = self.driver.current_window_handle
            self.driver.find_element_by_id('username').send_keys(auth.username_dt)
            self.driver.find_element_by_id('password').send_keys(auth.password_dt)
            self.driver.find_element_by_class_name("submit").click()
            self.driver.execute_script('window.open('');')
            self.ad_window = self.driver.window_handles[1]
            self.driver.switch_to_window(self.ad_window)
            self.driver.get(auth.auth_url_ad)
            self.driver.find_element_by_name('login').send_keys(auth.username_ad)
            self.driver.find_element_by_name('password').send_keys(auth.password_ad)
            self.driver.find_element_by_id("id_sign_in").click()
        else:
            self.chat_print(gui, 'Браузер уже запущен')

    def chat_print(self, gui, text):
        """Функция для вывода информации на экран. Активировать окно и добавить вывод через очередь"""
        gui.show_process()
        gui.chat.queue.put(gui.command_window.append(text))
        gui.command_window.moveCursor(QtGui.QTextCursor.End)

    def add_banner(self, gui):
        try:
            self.driver.switch_to_window(self.dt_window)
            wait = WebDriverWait(self.driver, 5, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="_____"]')))
            links = list(filter(lambda x: len(x.get_attribute('href')) > 150, links))
            links = set(map(lambda x: x.get_attribute('href'), links))
            links = list(links)
            links = sorted(links, key=lambda x: re.search(r'_____(\d+).', x).group(1))
            dir_name = self.driver.find_elements_by_css_selector('tr th')[0]
            dir_name = re.search(r'Хостинг файлов: (.*)', dir_name.text).group(1)
            self.chat_print(gui, f'В работе "{len(links)}" баннер(ов) из папки: {dir_name}')
            self.chat_print(gui, f'Дата начала акции:{self.start_data}, Дата окончания акции:'
                                 f'{self.end_data}, url: {self.url}')
            if not self.start_data:
                now = datetime.datetime.now()
                self.start_data = now.strftime('%d.%m.%Y')
            for link in links:
                if self.exit:
                    return
                self.driver.get(link)
                size = self.driver.find_element_by_css_selector('input[id*="geTitle"]').get_attribute('value')
                width = re.search(r'(\d+)__\d\d', size).group(1)
                height = re.search(r'__(\d+)x', size).group(1)
                width_field = self.driver.find_element_by_name('width')
                height_field = self.driver.find_element_by_name('height')
                start_data_field = self.driver.find_element_by_css_selector(
                    'input[name="graphicalElementTransport.startDate"]')
                end_data_field = self.driver.find_element_by_css_selector(
                    'input[name="graphicalElementTransport.endDate"]')
                url_field = self.driver.find_element_by_css_selector(
                    'textarea[name="graphicalElementTransport.description"]')
                width_field.clear()
                height_field.clear()
                width_field.send_keys(width)
                height_field.send_keys(height)
                self.driver.find_element_by_class_name('noDecoration').click()
                start_data_field.send_keys(self.start_data)
                end_data_field.send_keys(self.end_data)
                url_field.send_keys(self.url)
                sleep(1)
                self.driver.find_elements_by_css_selector('input[value="Предварительный"]')[1].click()
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[value="Сохранить"]'))).click()
                self.chat_print(gui, f'файл {size} успешно загружен')
            self.chat_print(gui, '#' * 60)
            self.chat_print(gui, '#' * 60)
            self.chat_print(gui, 'С первой папкой закончил, жду следующую')
        except WebDriverException as exc:
            self.chat_print(gui, f'Произошла ошибка {exc}: {exc.msg}')
            if 'chrome not reachable' in exc.msg:
                self.chat_print(gui, 'Браузер закрыт')
        except AttributeError as exc:
            self.chat_print(gui, 'Необходимо открыть папку с баннерами в браузере')

    def parser(self, gui):
        """Сбор и форамтирование информации об акциях"""
        try:
            for window in self.driver.window_handles:
                if window != self.dt_window and window != self.ad_window:
                    self.driver.switch_to.window(window)
            if len(self.driver.window_handles) == 2:
                self.driver.switch_to.window(self.ad_window)
            page = BeautifulSoup(self.driver.page_source, 'lxml')
            actions = page.findAll('div', class_='coupon')
            self.chat_print(gui, f'Всего будет обработано акций {len(actions)}')
            for act in actions:
                action = OrderedDict()
                action['Имя партнера'] = act.findAll('b', text=True)[1].text.strip()
                action['Название акции'] = act.find('p', {'class': 'h3-name'}).text.strip()
                full_date = act.find("b", text=re.compile('.*\s*(\d+.\d+.\d+)'))
                temp = ''.join(str(full_date.text).split())
                action['Дата начала'] = re.search(r'^(\d+.\d+.\d{4})', temp).group(1)
                action['Дата окончания'] = re.search(r'-(\d+.\d+.\d{4})', temp).group(1)
                action['Тип купона'] = re.sub(r'\s+', ' ', act.findAll('td', text=True)[4].text).strip()
                action['Условия акции'] = act.findAll('p', text=True)[1].text.strip() if \
                    len(act.findAll('p', text=True)) > 1 else ''
                self.actions_data.append(action)
            self.chat_print(gui, f'Акции успешно загружены в память')
            gui.show_process()
            for n, a in enumerate(self.actions_data, 1):
                self.chat_print(gui, f'\n---№{n}\n')
                for key, value in a.items():
                    gui.chat.queue.put(gui.command_window.append('{:_<20}: {}'.format(key, value)))
            if self.driver.current_window_handle != self.ad_window and \
                    self.driver.current_window_handle != self.dt_window:
                self.driver.close()
            self.driver.switch_to.window(self.ad_window)
            gui.show_process()
        except WebDriverException as exc:
            self.chat_print(gui, f'Произошла {exc}: {exc.msg}')
            if 'chrome not reachable' in exc.msg:
                self.chat_print(gui, f'Браузер закрыт {exc}, {exc.msg}')
        except AttributeError as exc:
            self.chat_print(gui, 'Нужно зайти на страницу с акциями')

    def add_actions(self, gui):
        """Добавление акций на основе полученных данных"""
        try:
            for action in self.actions_data:
                if self.exit:
                    return
                self.driver.switch_to_window(self.dt_window)
                url = self.driver.current_url
                id = re.search(r'Id=(\d+)', url).group(1)
                self.driver.switch_to_frame('ifrm')
                header = self.driver.find_element_by_name('title')
                vaucher_type = Select(self.driver.find_element_by_id('voucherTypeId'))
                form = self.driver.find_element_by_css_selector('form[id="createVoucherForm"]')
                checkbox = self.driver.find_element_by_id('isPercentage')
                description = self.driver.find_element_by_id('description')
                short_description = self.driver.find_element_by_name('shortDescription')
                discount_amount = self.driver.find_element_by_id('discountAmount')
                valid_from = self.driver.find_element_by_id('id_startDate')
                valid_to = self.driver.find_element_by_id('id_endDate')
                start_date = self.driver.find_element_by_id('id_publishStartDate')
                end_date = self.driver.find_element_by_id('id_publishEndDate')
                code = self.driver.find_element_by_id('code')
                landing_url = self.driver.find_element_by_id('landingUrl')
                header.send_keys(action['Название акции'] + '!')
                valid_from.clear()
                valid_from.send_keys(action['Дата начала'])
                valid_to.clear()
                valid_to.send_keys(action['Дата окончания'])
                start_date.clear()
                start_date.send_keys(action['Дата начала'])
                end_date.clear()
                end_date.send_keys(action['Дата окончания'])
                short_description.send_keys(action['Название акции'] + '!')
                if action['Условия акции']:
                    description.send_keys(action['Условия акции'] + '!')
                else:
                    description.send_keys(action['Название акции'] + '!')
                landing_url.send_keys(gui.url.toPlainText())
                if 'скидка' in action['Тип купона'].lower() or 'купон' in action['Тип купона'].lower():
                    vaucher_type.select_by_value('2') if 'скидка' in action['Тип купона'].lower() \
                        else vaucher_type.select_by_value('1')
                    code.send_keys('Не требуется')
                    if '%' in action['Название акции']:
                        checkbox.click()
                        percent = self.get_percent(action['Название акции'])
                        discount_amount.send_keys(percent)
                    elif '%' in action['Условия акции']:
                        checkbox.click()
                        percent = self.get_percent(action['Условия акции'])
                        discount_amount.send_keys(percent)
                    else:
                        discount_amount.send_keys('0')
                elif 'подарок' in action['Тип купона'].lower():
                    vaucher_type.select_by_value('3')
                    code.send_keys('Не требуется')
                elif 'доставка' in action['Тип купона'].lower():
                    vaucher_type.select_by_value('4')
                    code.send_keys('Не требуется')
                form.submit()
                self.driver.switch_to_default_content()
                sleep(1)
                self.driver.find_element_by_id('VOUCHERS_MERCHANT_AD_MANAGEMENT_VOUCHERS_CREATE').click()
                self.driver.get(auth.coupun_url + id)
            self.actions_data.clear()
            self.chat_print(gui, 'Акции успешно добавлены, буфер очищен')
        except WebDriverException as exc:
            self.chat_print(gui, '*' * 60)
            self.chat_print(gui, f'Данные об акциях были очищены, нужно загрузить снова')
            self.actions_data.clear()
        except AttributeError as exc:
            self.chat_print(gui, '*' * 60)
            self.chat_print(gui, f'Данные об акциях были очищены, нужно загрузить снова')
            self.actions_data.clear()

    def get_percent(self, action):
        try:
            percent = re.search(r'(\d+)%', action).group(1)
        except AttributeError:
            percent = re.search(r'%(\d+)', action).group(1)
        return percent

    def download_banners(self, gui):
        """Загрузка баннеров с сайта"""
        try:
            for window in self.driver.window_handles:
                if window != self.dt_window and window != self.ad_window:
                    self.driver.switch_to.window(window)
            if len(self.driver.window_handles) == 2:
                self.driver.switch_to.window(self.ad_window)
            wait = WebDriverWait(self.driver, 5, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[class="banner_view"]')))
            links = set(map(lambda x: x.get_attribute('href'), links))
            links = list(links)
            if links:
                home_path = os.getenv('HOMEPATH')
                result = os.path.join('C:\\', home_path, 'Desktop', 'result')
                result = os.path.normpath(result)
                if not os.path.exists(result):
                    os.mkdir(result)
                self.chat_print(gui, f'Всего будет скачано {len(links)} баннеров')
                self.chat_print(gui, f'Результаты здесь: {os.path.abspath(result)}')
                for link in links:
                    format = re.search(r'(\w+)$', link).group(1)
                    name = str(self.name_index) + "." + format
                    self.name_index += 1
                    path = os.path.join(result, name)
                    p = requests.get(link)
                    out = open(path, 'wb')
                    out.write(p.content)
                    out.close()
                    self.chat_print(gui, f'{name} успешно скачан\n')
                self.chat_print(gui, f'Загрузка успешно завершена')
            else:
                self.chat_print(gui, 'Нужно зайти на страницу с баннерами')

        except WebDriverException as exc:
            self.chat_print(gui, f'Произошла {exc}: {exc.msg}')
            if 'chrome not reachable' in exc.msg:
                self.chat_print(gui, f'Браузер закрыт {exc}, {exc.msg}')
        except AttributeError as exc:
            self.chat_print(gui, 'Нужно зайти на страницу с баннерами')

    def parser_sephora(self, gui):
        """Сбор и форамтирование информации об акциях"""

        def get_date(self, div):
            incoming_date = re.search(r'Срок проведения Акции: с (\d.*\d+)', div.text)[1]
            day, month, year = incoming_date.split(" ")
            for num, name in self.month_name.items():
                if name in month.lower():
                    month = num
            date_start = datetime(day=int(day), month=int(month), year=int(year)).strftime('%d.%m.%Y')
            day_on_month = monthrange(year=int(year), month=int(month))
            end_data = datetime(day=day_on_month[1], month=int(month), year=int(year)).strftime('%d.%m.%Y')
            return date_start, end_data

        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        })
        main_url = 'https://sephora.ru/news/'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        links = page.find_all("a", class_='b-news-thumb__title')
        for link in links:
            link = main_url[:-5] + link['href'][1:]
            request = s.get(link)
            page = BeautifulSoup(request.text, 'lxml')
            div = page.find('div', class_='b-news-detailed')
            if div:
                try:
                    date_start, date_end = get_date(self, div)
                except TypeError as exc:
                    gui.log.info('Не найдена дата проведения акции')
                    continue
                action_name = div.h1.text
                paragraphs = div.findAll('p')
                descriptions = []
                for p in paragraphs:
                    text = p.text.strip()
                    if 'При' in text:
                        descriptions.append(text)
                for desc in descriptions:

                    print(f'Заголовок: {action_name}')
                    print(f'Начало акции: {date_start}')
                    print(f'Окончание акции: {date_end}')
                    print(f'Полное описание: {desc}')
                    print(f'Короткое описание: {action_name}')
                    print(f'Купон: Не требуется')
                    print(f'URL: https://sephora.ru')
        # TODO подготовить вывод результатов для запись в таблицу csv
