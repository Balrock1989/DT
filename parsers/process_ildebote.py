from datetime import datetime, timedelta
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup
import helpers.helper as helper


class Ildebote_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "ИльДэБотэ"

    def run(self):
        partner_name = 'ИльДэБотэ'
        actions_data = []
        url = 'https://iledebeaute.ru/company/actions/'
        page = helper.prepair_parser_data_use_request(url)
        divs = page.find_all("div", class_='news_block')
        for div in divs:
            date = div.find("p", class_='date')
            if 'сегодня' not in date.text.strip().lower() and 'вчера' not in date.text.strip().lower():
                continue
            name = div.h2.text
            try:
                start, end = helper.convert_list_to_date(helper.get_range_date(name))
            except Exception:
                start = helper.DATA_NOW
                end = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')

            desc = div.find("p", class_='desc').text.strip()
            code = 'Не требуется'
            if helper.promotion_is_outdated(end):
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
