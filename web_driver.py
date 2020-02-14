import csv
import os
import re
import shutil
import threading
from collections import OrderedDict
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException, \
    NoSuchFrameException, NoSuchElementException
import auth
import helpers.helper as helper

from helpers import win32


# TODO Писать сколько акций добавлено после add actions
# TODO Добавить комменты

class WebDriver:

    def __init__(self, gui):
        self.start_data = ''
        self.end_data = ''
        self.url = ''
        self.driver = None
        self.exit = False
        self.dt_window = None
        self.ad_window = None
        self.actions_data = []
        self.name_index = 1
        self.gui = gui

    def auth(self):
        """Запуск браузера и авторизация на сайтах"""
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        win32.hide_chrome_console()
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

    @win32.show_window
    def add_banner(self):
        """Загрузка баннеров на сервер"""
        self.driver.switch_to_window(self.dt_window)
        try:
            wait = WebDriverWait(self.driver, 1, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="_____"]')))
        except TimeoutException:
            self.gui.chat_print_signal.emit('Нужно зайти на страницу с баннерами')
            win32.show_process()
            return
        links = list(filter(lambda x: len(x.get_attribute('href')) > 150, links))
        links = set(map(lambda x: x.get_attribute('href'), links))
        links = list(links)
        links = sorted(links, key=lambda x: re.search(r'_____(\d+).', x).group(1))
        dir_name = self.driver.find_elements_by_css_selector('tr th')[0]
        dir_name = re.search(r'Хостинг файлов: (.*)', dir_name.text).group(1)
        self.gui.chat_print_signal.emit(f'В работе "{len(links)}" баннер(ов) из папки: {dir_name}')
        self.gui.chat_print_signal.emit(f'Дата начала акции:{self.start_data},'
                                        f' Дата окончания акции:{self.end_data}, url: {self.url}')
        if not self.start_data:
            self.start_data = helper.DATA_NOW
        self.gui.change_progress_signal.emit(len(links))
        for link in links:
            if self.exit:
                self.gui.chat_print_signal.emit(f'Загрузка прервана пользователем')
                win32.show_process()
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
            self.driver.find_elements_by_css_selector('input[value="Предварительный"]')[1].click()
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[value="Сохранить"]'))).click()
            self.gui.chat_print_signal.emit(f'файл {size} успешно загружен')
            self.gui.queue.queue.put('progress')
        self.gui.chat_print_signal.emit('#' * 60)
        self.gui.chat_print_signal.emit('Загрузка завершена')

    @win32.show_window
    def parser(self):
        """Сбор и форамтирование информации об акциях"""
        self.driver.switch_to_window(self.dt_window)
        for window in self.driver.window_handles:
            if window != self.dt_window and window != self.ad_window:
                self.driver.switch_to.window(window)
        if len(self.driver.window_handles) == 2:
            self.driver.switch_to.window(self.ad_window)
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        actions = page.findAll('div', class_='coupon')
        self.gui.chat_print_signal.emit(f'Всего будет обработано акций {len(actions)}')
        partner_name = ''
        if actions:
            self.gui.change_progress_signal.emit(len(actions))
            for act in actions:
                action = OrderedDict()
                action['Имя партнера'] = act.findAll('b', text=True)[1].text.strip()
                partner_name = action['Имя партнера']
                action['Название акции'] = act.find('p', {'class': 'h3-name'}).text.strip()
                now = datetime.now()
                try:
                    full_date = act.find("b", text=re.compile('.*\s*(\d+.\d+.\d+)')).text.strip()
                except AttributeError:
                    date_end = now + timedelta(days=180)
                    full_date = str(now.strftime('%d.%m.%Y')) + "-" + date_end.strftime('%d.%m.%Y')
                temp = ''.join(str(full_date).split())
                action['Дата начала'] = re.search(r'^(\d+.\d+.\d{4})', temp).group(1)
                action['Дата окончания'] = re.search(r'-(\d+.\d+.\d{4})', temp).group(1)
                date_start = datetime.strptime(action['Дата начала'], '%d.%m.%Y')
                date_end = datetime.strptime(action['Дата окончания'], '%d.%m.%Y')
                diff_date = date_end - date_start
                if diff_date.days > 180:
                    action['Дата окончания'] = date_start + timedelta(days=180)
                action['Тип купона'] = re.sub(r'\s+', ' ', act.findAll('td', text=True)[4].text).strip()
                action['Условия акции'] = act.findAll('p', text=True)[1].text.strip() if \
                    len(act.findAll('p', text=True)) > 1 else ''
                self.actions_data.append(action)
                self.gui.queue.queue.put(helper.write_csv(action))
                self.gui.queue.queue.put('progress')
            self.gui.set_partner_name_signal.emit(partner_name)
            for n, a in enumerate(self.actions_data, 1):
                self.gui.chat_print_signal.emit(f'---№{n}\n')
                action = ''
                for key, value in a.items():
                    action = action + "".join('{:_<20}: {}\n'.format(key, value))
                self.gui.chat_print_signal.emit(action)
            if self.driver.current_window_handle != self.ad_window and \
                    self.driver.current_window_handle != self.dt_window:
                self.driver.close()
            self.driver.switch_to.window(self.ad_window)
            self.gui.chat_print_signal.emit('Акции успешно загружены')
            self.actions_data.clear()
        else:
            self.gui.chat_print_signal.emit('Нужно зайти на страницу с акциями')

    @win32.show_window
    def add_actions(self):
        """Добавление акций на основе полученных данных"""

        def get_percent(action):
            if "%" in action:
                try:
                    percent = re.search(r'(\d+)%', action).group(1)
                except AttributeError:
                    percent = re.search(r'%(\d+)', action).group(1)
            else:
                percent = re.search(r'(\d+\s?\d+)', action).group(1).replace(' ', '')
            return percent

        def add():
            partner_name = ''
            with open(helper.actions_csv_path, 'r', encoding='utf-8', newline='') as csv_file:
                csv_data = csv.DictReader(csv_file, delimiter=';')
                suitable_actions = [action for action in csv_data if action['Имя партнера'] == self.gui.partner_name.currentText()]
            count = len(suitable_actions)
            self.gui.change_progress_signal.emit(count)
            with open(helper.actions_csv_path, 'r', encoding='utf-8', newline='') as csv_file:
                csv_data = csv.DictReader(csv_file, delimiter=';')
                for action in csv_data:
                    if self.exit:
                        self.gui.chat_print_signal.emit('Процесс был прерван пользователем.')
                        win32.show_process()
                        return
                    self.driver.switch_to_window(self.dt_window)
                    url = self.driver.current_url
                    try:
                        id = re.search(r'Id=(\d+)', url).group(1)
                        self.driver.switch_to_frame('ifrm')
                        header = self.driver.find_element_by_name('title')
                    except (NoSuchFrameException, NoSuchElementException, AttributeError):
                        self.gui.chat_print_signal.emit('*' * 60)
                        self.gui.chat_print_signal.emit(f'Парсер  AD запущен не на той странице')
                        win32.show_process()
                        return
                    if action['Имя партнера'] != self.gui.partner_name.currentText():
                        with open("actions_temp.csv", "a", newline="", encoding="utf-8") as csv_file:
                            writer = csv.DictWriter(csv_file, fieldnames=helper.HEADERS, delimiter=";")
                            writer.writerow(action)
                        continue
                    partner_name = action['Имя партнера']
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
                    digit_in_name, digit_in_desc = '', ''
                    try:
                        digit_in_name = re.search(r'(\d+)', action['Название акции']).group(1).strip()
                    except Exception:
                        pass
                    try:
                        digit_in_desc = re.search(r'(\d+)', action['Условия акции']).group(1).strip()
                    except Exception:
                        pass
                    if action['Условия акции']:
                        description.send_keys(action['Условия акции'] + '!')
                    else:
                        description.send_keys(action['Название акции'] + '!')
                    landing_url.send_keys(self.gui.url.toPlainText()) if \
                        self.gui.url.toPlainText() else landing_url.send_keys(action['URL'])
                    if 'скидка' in action['Тип купона'].lower():
                        vaucher_type.select_by_value('2')
                        code.send_keys(action['Купон']) if action['Купон'] else code.send_keys('Не требуется')
                        if '%' in action['Название акции']:
                            checkbox.click()
                            percent = get_percent(action['Название акции'])
                            discount_amount.send_keys(percent)
                        elif '%' in action['Условия акции']:
                            checkbox.click()
                            percent = get_percent(action['Условия акции'])
                            discount_amount.send_keys(percent)
                        elif digit_in_name:
                            discount_amount.send_keys(digit_in_name)
                        elif digit_in_desc:
                            discount_amount.send_keys(digit_in_desc)
                        else:
                            discount_amount.send_keys("0")
                    elif 'купон' in action['Тип купона'].lower():
                        vaucher_type.select_by_value('1')
                        code.send_keys(action['Купон']) if action['Купон'] else code.send_keys('Не требуется')
                        if '%' in action['Название акции']:
                            checkbox.click()
                            percent = get_percent(action['Название акции'])
                            discount_amount.send_keys(percent)
                        elif '%' in action['Условия акции']:
                            checkbox.click()
                            percent = get_percent(action['Условия акции'])
                            discount_amount.send_keys(percent)
                        elif digit_in_name in action['Название акции']:
                            discount_amount.send_keys(digit_in_name)
                        elif digit_in_desc in action['Условия акции']:
                            discount_amount.send_keys(digit_in_desc)
                        else:
                            discount_amount.send_keys("0")
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
                    self.gui.queue.queue.put('progress')
            os.remove(helper.actions_csv_path)
            shutil.move('actions_temp.csv', helper.actions_csv_path)
            self.gui.del_partner_name_signal.emit(partner_name)
            self.gui.chat_print_signal.emit(f'Акции успешно добавлены ({count}шт.)') if count \
                else self.gui.chat_print_signal.emit('Нет акций выбранного партнера')
            win32.show_process()
        helper.generate_temp_csv()
        self.driver.switch_to_window(self.dt_window)
        threading.Thread(target=add, args=(), daemon=True).start()

    @win32.show_window
    def download_banners(self):
        """Загрузка баннеров с сайта"""

        def run(link):
            format = re.search(r'(\w+)$', link).group(1)
            name = str(self.name_index) + "." + format
            self.name_index += 1
            path = os.path.join(helper.result_path, name)
            p = requests.get(link)
            out = open(path, 'wb')
            out.write(p.content)
            out.close()
            self.gui.chat_print_signal.emit(f'{name} успешно скачан')

        for window in self.driver.window_handles:
            if window != self.dt_window and window != self.ad_window:
                self.driver.switch_to.window(window)
        if len(self.driver.window_handles) == 2:
            self.driver.switch_to.window(self.ad_window)
        try:
            wait = WebDriverWait(self.driver, 2, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[class="banner_view"]')))
        except TimeoutException:
            self.gui.chat_print_signal.emit('Нужно зайти на страницу с баннерами')
            win32.show_process()
            return
        links = set(map(lambda x: x.get_attribute('href'), links))
        links = list(links)
        if links:
            if self.exit:
                self.gui.chat_print_signal.emit('Процесс был прерван пользователем.')
                win32.show_process()
                return
            if not os.path.exists(helper.result_path):
                os.mkdir(helper.result_path)
            self.gui.chat_print_signal.emit(f'Всего будет скачано {len(links)} баннеров')
            self.gui.chat_print_signal.emit(f'Результаты здесь: {os.path.abspath(helper.result_path)}')
            threads = [threading.Thread(target=run, args=(link,), daemon=True) for link in links]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.gui.chat_print_signal.emit('Загрузка завершена')
        else:
            self.gui.chat_print_signal.emit('Баннеры не найдены на этой странице')
