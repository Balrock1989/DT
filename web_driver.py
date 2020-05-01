import csv
import os
import re
import shutil
import threading
from time import sleep

from PyQt5.QtCore import QThread
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
from database.data_base import actions_exists_in_db

from helpers import win32


class WebThread(QThread):
    """Отдельный поток для работы браузера"""

    def __init__(self, mainwindow):
        super(WebThread, self).__init__()
        self.mainwindow = mainwindow
        self.web = WebDriver(mainwindow)
        mainwindow.browser = self.web
        self.web.start_data = self.mainwindow.date_start.toPlainText()
        self.web.end_data = self.mainwindow.date_end.toPlainText()
        self.web.url = self.mainwindow.url.toPlainText()

    def run(self):
        self.web.auth()


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
        self.gui = gui
        self.ignore = gui.ignore_database
        self.queue = gui.queue.queue

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

        def run(links):
            for link in links:
                if self.exit:
                    self.queue.put(f'Загрузка прервана пользователем')
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
                self.queue.put(f'файл {size} успешно загружен')
                self.queue.put('progress')
            self.queue.put('#' * 60)
            self.queue.put('Загрузка завершена')

        self.driver.switch_to_window(self.dt_window)
        try:
            wait = WebDriverWait(self.driver, 1, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="_____"]')))
        except TimeoutException:
            self.queue.put('Нужно зайти на страницу с баннерами')
            win32.show_process()
            return
        links = list(filter(lambda x: len(x.get_attribute('href')) > 150, links))
        links = set(map(lambda x: x.get_attribute('href'), links))
        links = list(links)
        links = sorted(links, key=lambda x: re.search(r'_____(\d+).', x).group(1))
        dir_name = self.driver.find_elements_by_css_selector('tr th')[0]
        dir_name = re.search(r'Хостинг файлов: (.*)', dir_name.text).group(1)
        self.queue.put(f'В работе "{len(links)}" баннер(ов) из папки: {dir_name}')
        self.queue.put(f'Дата начала акции:{self.start_data}, Дата окончания акции:{self.end_data}, url: {self.url}')
        if not self.start_data:
            self.start_data = helper.DATA_NOW
        self.gui.change_progress_signal.emit(len(links))
        thread = threading.Thread(target=run, args=(links,), daemon=True)
        thread.start()
        thread.join()

    @win32.show_window
    def parser(self):
        """Сбор и форамтирование информации об акциях"""
        self.driver.switch_to_window(self.dt_window)
        lock = threading.Lock()
        for window in self.driver.window_handles:
            if window != self.dt_window and window != self.ad_window:
                self.driver.switch_to.window(window)
        if len(self.driver.window_handles) == 2:
            self.driver.switch_to.window(self.ad_window)
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        actions = page.findAll('div', class_='coupon')
        self.queue.put(f'Всего будет обработано акций {len(actions)}')
        partner = ''
        if actions:
            self.gui.change_progress_signal.emit(len(actions))
            for act in actions:
                partner = act.findAll('b', text=True)[1].text.strip()
                name = act.find('p', {'class': 'h3-name'}).text.strip()
                now = datetime.now()
                try:
                    full_date = act.find("b", text=re.compile('.*\s*(\d+.\d+.\d+)')).text.strip()
                except AttributeError:
                    end = now + timedelta(days=180)
                    full_date = str(now.strftime('%d.%m.%Y')) + "-" + end.strftime('%d.%m.%Y')
                temp = ''.join(str(full_date).split())
                url = ''
                code = ''
                short_desc = ''
                start = datetime.strptime(re.search(r'^(\d+.\d+.\d{4})', temp).group(1), '%d.%m.%Y')
                end = datetime.strptime(re.search(r'-(\d+.\d+.\d{4})', temp).group(1), '%d.%m.%Y')
                diff_date = end - start
                if diff_date.days > 180:
                    end = start + timedelta(days=180)
                start = start.strftime('%d.%m.%Y')
                end = end.strftime('%d.%m.%Y')
                action_type = re.sub(r'\s+', ' ', act.findAll('td', text=True)[4].text).strip()
                desc = act.findAll('p', text=True)[1].text.strip() if \
                    len(act.findAll('p', text=True)) > 1 else ''
                if not self.ignore.isChecked():
                    with lock:
                        if actions_exists_in_db(partner, name, start, end):
                            continue
                action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
                self.actions_data.append(action)
                self.queue.put('progress')
            if len(self.actions_data) == 0:
                self.queue.put(f'Акции по {partner} не найдены ')
            else:
                self.queue.put(helper.write_csv(self.actions_data))
                self.queue.put((partner,))
                self.queue.put(self.actions_data)
            if self.driver.current_window_handle != self.ad_window and \
                    self.driver.current_window_handle != self.dt_window:
                self.driver.close()
            self.driver.switch_to.window(self.ad_window)
            self.actions_data.clear()
        else:
            self.queue.put('Нужно зайти на страницу с акциями')

    @win32.show_window
    def add_actions(self):
        """Добавление акций на основе полученных данных"""
        def add():
            partner_name = ''
            count = helper.get_count_suitable_actions(self.gui)
            self.gui.change_progress_signal.emit(count)
            with open(helper.actions_csv_path, 'r', encoding='utf-8', newline='') as csv_file:
                csv_data = csv.DictReader(csv_file, delimiter=';')
                for action in csv_data:
                    self.driver.switch_to_window(self.dt_window)
                    url = self.driver.current_url
                    if self.exit:
                        self.queue.put('Процесс был прерван пользователем.')
                        win32.show_process()
                        return
                    try:
                        id = re.search(r'Id=(\d+)', url).group(1)
                        self.driver.switch_to_frame('ifrm')
                        header = self.driver.find_element_by_name('title')
                    except (NoSuchFrameException, NoSuchElementException, AttributeError):
                        self.queue.put('*' * 60)
                        self.queue.put(f'Парсер  AD запущен не на той странице')
                        win32.show_process()
                        return
                    # Акции которые есть в CSV но не подходят по партнеру записываем во временный файл, чтобы сохранить.
                    if self.gui.partner_name.count() > 0 and action['Имя партнера'] != self.gui.partner_name.currentText():
                        with open("actions_temp.csv", "a", newline="", encoding="utf-8") as csv_file:
                            writer = csv.DictWriter(csv_file, fieldnames=helper.HEADERS, delimiter=";")
                            writer.writerow(action)
                        continue
                    form = self.driver.find_element_by_css_selector('form[id="createVoucherForm"]')
                    partner_name = action['Имя партнера']
                    self.fill_field_actions(action, header)
                    form.submit()
                    self.driver.switch_to_default_content()
                    sleep(1)
                    self.driver.find_element_by_id('VOUCHERS_MERCHANT_AD_MANAGEMENT_VOUCHERS_CREATE').click()
                    self.driver.get(auth.coupun_url + id)
                    self.gui.queue.queue.put('progress')
            os.remove(helper.actions_csv_path)
            shutil.move('actions_temp.csv', helper.actions_csv_path)
            self.gui.del_partner_name_signal.emit(partner_name)
            self.queue.put(f'Акции успешно добавлены ({count} шт.)') if count else \
                self.queue.put('Нет акций выбранного партнера')
            self.gui.reset_progress_signal.emit()
            win32.show_process()

        helper.generate_temp_csv()
        self.driver.switch_to_window(self.dt_window)
        threading.Thread(target=add, args=(), daemon=True).start()

    @win32.show_window
    def download_banners(self):
        """Загрузка баннеров с сайта"""
        for window in self.driver.window_handles:
            if window != self.dt_window and window != self.ad_window:
                self.driver.switch_to.window(window)
        if len(self.driver.window_handles) == 2:
            self.driver.switch_to.window(self.ad_window)
        try:
            wait = WebDriverWait(self.driver, 2, poll_frequency=0.5, ignored_exceptions=UnexpectedAlertPresentException)
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[class="banner_view"]')))
        except TimeoutException:
            self.queue.put('Нужно зайти на страницу с баннерами')
            win32.show_process()
            return
        links = set(map(lambda x: x.get_attribute('href'), links))
        links = list(links)
        helper.banner_downloader(links, self.gui.queue.queue)

    def fill_field_actions(self, action, header):

        def get_percent(action):
            try:
                return re.search(r'(\d+)\s?%', action).group(1)
            except AttributeError:
                return re.search(r'%\s?(\d+)', action).group(1)

        if self.gui.partner_name.count() == 0:
            action['Название акции'] = action['Название акции'] + action['Сумма скидки']
        if "не требуется" not in action['Купон'].lower() and action['Купон'] != "-":
            action['Тип купона'] = "Купон"
        vaucher_type = Select(self.driver.find_element_by_id('voucherTypeId'))
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
        short_description.send_keys(action['Короткое описание'] + '!') if action['Короткое описание'] \
            else short_description.send_keys(action['Название акции'] + '!')
        digit_in_name = helper.check_digit(action['Название акции'])
        digit_in_desc = helper.check_digit(action['Условия акции'])
        if action['Условия акции']:
            description.send_keys(action['Условия акции'] + '!')
        else:
            description.send_keys(action['Название акции'] + '!')
        landing_url.send_keys(self.gui.url.toPlainText()) if \
            self.gui.url.toPlainText() else landing_url.send_keys(action['URL'])
        if 'скидка' in action['Тип купона'].lower():
            vaucher_type.select_by_value('2')
            code.send_keys(action['Купон']) if action['Купон'] and \
                                               action['Купон'] != "-" else code.send_keys('Не требуется')
            if '%' in action['Название акции']:
                percent = get_percent(action['Название акции'])
                if percent != '0':
                    checkbox.click()
                discount_amount.send_keys(percent)
            elif '%' in action['Условия акции']:
                percent = get_percent(action['Условия акции'])
                if percent != '0':
                    checkbox.click()
                discount_amount.send_keys(percent)
            elif digit_in_name:
                discount_amount.send_keys(digit_in_name)
            elif digit_in_desc:
                discount_amount.send_keys(digit_in_desc)
            else:
                discount_amount.send_keys("0")
        elif 'купон' in action['Тип купона'].lower():
            vaucher_type.select_by_value('1')
            code.send_keys(action['Купон']) if action['Купон'] and \
                                               action['Купон'] != "-" else code.send_keys('Не требуется')
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
