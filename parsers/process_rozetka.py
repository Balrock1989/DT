import re
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Rozetka_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Розетка"

    def run(self):
        partner_name = 'Розетка'
        actions_data = []
        for i in range(1, 41):
            main_url = f'https://rozetka.com.ua/news-articles-promotions/promotions/page={i}'
            page = helper.get_page_use_request(main_url)
            divs = page.find_all('div', class_='promo-cat-i')
            for div in divs:
                if div.get('name') == 'more_promotions':
                    continue
                url = div.find('a').get('href')
                name = div.find('div', class_='promo-cat-i-summary').text.strip()
                try:
                    date = div.find('time', class_='promo-cat-i-date').text.strip()
                    date = re.sub(r'\xa0', ' ', date).strip()
                    start, end = helper.search_data_in_text(date)
                except:
                    start, end = helper.get_date_now_to_end_month()
                code = "Не требуется"
                desc = name
                short_desc = ''
                action_type = helper.check_action_type(code, name, desc)
                if helper.promotion_is_outdated(end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db(partner_name, name, start, end):
                        continue
                action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type,short_desc)
                actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
