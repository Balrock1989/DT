import os
import re
import threading
from random import randint
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from urllib3.exceptions import RequestError
from webdriver_manager.chrome import ChromeDriverManager

from helpers import Win32
from helpers.Paths import RESULT_PATH


class ActionsUtil:

    def __init__(self, queue):
        self.queue = queue

    def check_action_type(self, action):
        if 'требуется' not in action.code:
            action_type = 'купон'
        elif 'подарок' in action.name.lower() or 'подарок' in action.desc.lower():
            action_type = 'подарок'
        elif 'доставка' in action.desc.lower() or 'доставка' in action.desc.lower():
            action_type = 'доставка'
        else:
            action_type = 'скидка'
        return action_type

    def get_page_use_webdriver(self, url, scroll=False, quit=True, hidden=False):
        """Делает запрос на URL и возвращает BS объект страницы используя webdriver, с возможностью скролить страницу"""
        driver = None
        if hidden:
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--headless")
            try:
                driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
            except SessionNotCreatedException:
                self.queue.put('Необходимо обновить версию драйвера https://chromedriver.chromium.org/')
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), )
        Win32.hide_all_chromedriver()
        driver.get(url)
        if scroll:
            scroll_script = \
                "window.scrollTo(0, document.body.scrollHeight);var len_of_page=document.body.scrollHeight;return " \
                "len_of_page; "
            len_of_page = driver.execute_script(scroll_script)
            while True:
                last_count = len_of_page
                sleep(1)
                len_of_page = driver.execute_script(scroll_script)
                if last_count == len_of_page:
                    break
        page = BeautifulSoup(driver.page_source, 'lxml')
        if quit:
            driver.quit()
            return page
        else:
            return page, driver

    def get_webdriver(self, hidden=True):
        """Делает запрос на URL и возвращает BS объект страницы используя webdriver, с возможностью скролить страницу"""
        driver = None
        if hidden:
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--headless")
            try:
                driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
            except SessionNotCreatedException:
                self.queue.put('Необходимо обновить версию драйвера https://chromedriver.chromium.org/')
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), )
        Win32.hide_all_chromedriver()
        return driver

    def get_page_with_driver(self, driver, main_url):
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        return page

    def get_page_use_request(self, url):
        """Делает запрос на URL и возвращает BS объект страницы используя библиотеку request"""
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', })
        try:
            request = s.get(url, timeout=3)
        except RequestError as exc:
            print(f'Не удалось выполнить запрос к {url}')
            raise exc
        return BeautifulSoup(request.text, 'lxml')

    def start_join_threads(self, threads):
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def banner_downloader(self, links, queue):
        """Загрузка баннеров с сайта"""
        if links:
            if not os.path.exists(RESULT_PATH):
                os.mkdir(RESULT_PATH)
            queue.put(f'Всего будет скачано {len(links)} баннеров')
            queue.put(f'Результаты здесь: {os.path.abspath(RESULT_PATH)}')

            threads = [threading.Thread(target=self.downloader_run, args=(link, queue), daemon=True) for link in links]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            queue.put('Загрузка завершена')
        else:
            queue.put('Баннеры не найдены на этой странице')

    def downloader_run(self, link, queue):
        """Принимает ссылку на баннер http"//......jpg и скачивает ее, запускается из banner_downloader в потоках"""
        name = randint(1000000, 9999999)
        file_format = re.search(r'(\w+)$', link).group(1)
        name = str(name) + "." + file_format
        path = os.path.join(RESULT_PATH, name)
        try:
            p = requests.get(link, timeout=5)
            out = open(path, 'wb')
            out.write(p.content)
            out.close()
            queue.put(f'{name} успешно скачан')
        except Exception as exc:
            queue.put(f'Не удалось скачать баннер: {link}')
            print(exc)

    def generate_action(self, action):
        """Сборка акции для дальнейшей записи в CSV"""
        return {'Имя партнера': action.partner_name,
                'Название акции': action.name,
                'Дата начала': action.start,
                'Дата окончания': action.end,
                'Условия акции': action.desc,
                'Купон': action.code,
                'URL': action.url,
                'Тип купона': action.action_type,
                'Короткое описание': action.short_desc}

    def check_digit(self, text):
        """Принимает текст, ищет в нем все цифры и по одному слову слева и справа. Возвращает цифру по шаблону"""
        """ Возможные комбинации Скидка 1000 ₽, Скидка 1000₽, Скидка 1 000 руб, Скидка 1000 руб, Скидка 1000руб"""
        lists = re.findall(r'\w+\s\d+\s?\d+\s?\w+', text)
        lists2 = re.findall(r'\w+\s\d+\s?\d+\s?\W', text)
        lists = lists + lists2
        for string in lists:
            digit = re.sub(r'\D', '', string)
            if len(string.split()) == 4:
                digit = string.split()
                digit = digit[1] + " " + digit[2]
            if f'от {digit} руб' in string:
                continue
            if f'{digit} руб' in string or f'{digit}руб' in string:
                return digit.replace(' ', '')
            elif f'{digit} ₽' in string or f'{digit}₽' in string:
                return digit.replace(' ', '')
            else:
                continue
        return '0'

    def find_promo_code(self, text):
        """Принимает текст, по слову промокод ищет код стоящий после слова"""
        promo = re.findall(r'\bпромокод[а-я]*?\b\s\"?\«?\'?(\w+)', text)
        return promo[0] if promo else 'Не требуется'

    def check_exists_by_css(self, driver, css):
        try:
            elem = driver.find_element_by_css_selector(css)
        except NoSuchElementException:
            return False
        return elem
