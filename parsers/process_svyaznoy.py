import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Svyaznoy_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Связной"

    def run(self):
        partner_name = 'Связной'
        actions_data = []
        main_url = 'https://www.svyaznoy.ru/special-offers'
        page, driver = helper.get_page_use_webdriver(main_url, quit=False)
        divs = page.find_all('div', class_='b-article-preview__inner')
        links = []
        for div in divs:
            links.append(div.find('a', class_='b-article-preview__link').get('href'))
        self.queue.put(f'set {len(links)}')
        for link in links:
            driver.get(link)
            page = BeautifulSoup(driver.page_source, 'lxml')
            name = page.h1.text
            date = page.find('div', class_='b-event-info__item').find_all('span', class_='b-event-info__date')
            if len(date) == 2:
                start = helper.get_one_date(date[0].text.strip())
                end = helper.get_one_date(date[1].text.strip())
            elif len(date) == 1:
                start = helper.get_one_date(date[0].text.strip())
                end = helper.get_date_end_month()
            else:
                print(date)
            url = link
            desc = page.find('div', class_='b-article').text.strip()
            desc = re.sub(r'\s{2,}', ' ', desc).strip()
            code = helper.find_promo_code(desc)
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if helper.promotion_is_outdated(end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db(partner_name, name, start, end):
                    self.queue.put('progress')
                    continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
            self.queue.put('progress')
        driver.quit()
        helper.filling_queue(self.queue, actions_data, partner_name)



