import re
from multiprocessing import Process
from time import sleep

from bs4 import BeautifulSoup

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Interes_1c_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "1С_Интерес"

    def run(self):
        partner_name = '1С_Интерес'
        actions_data = []
        page, driver = helper.get_page_use_webdriver('https://www.1c-interes.ru/special_actions/', quit=False)
        for i in range(0, 5):
            next_btn = helper.check_exists_by_css(driver, '.news-next-btn')
            if next_btn:
                next_btn.click()
                sleep(1)
        page = BeautifulSoup(driver.page_source, 'lxml')
        divs = page.find_all("div", class_='main-holder')
        begin_url = 'https://www.1c-interes.ru'
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            url = begin_url + div.a.get('href').strip()
            name = div.h2.text.strip()
            try:
                date = div.find('div', class_='preorder-active-to').text.strip()
                start, end = helper.get_do_period(date)
            except:
                start = helper.DATA_NOW
                end = helper.get_date_end_month()
            desc = div.find('div', class_='h2 tile-hide').text.strip()
            code = 'Не требуется'
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
        helper.filling_queue(self.queue, actions_data, partner_name)
