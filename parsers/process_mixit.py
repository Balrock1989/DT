import re
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Mixit_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.link_selector = '.SpecialOfferPreview-media a'

    def __str__(self):
        return "Mixit"

    def run(self):
        partner_name = 'Mixit'
        actions_data = []
        url_base = 'https://mixit.ru'
        page = helper.get_page_use_webdriver('https://mixit.ru/special-offers', hidden=True)
        divs = page.select('.SpecialOfferList-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            if div.select_one(self.link_selector) is None:
                continue
            url = url_base + div.select_one(self.link_selector).get('href').strip()
            name = div.select_one('.Media-picture').get('alt').strip()
            start, end = helper.get_date_now_to_end_month()
            try:
                date = div.select_one('.SpecialOfferPreview-expireCaption').text.strip()
                if 'дне' in date:
                    day_end_action = re.search(r'(\d+)', date)
                    end = helper.get_date_plus_days(int(day_end_action.group(1)))
                elif 'месяц' in date:
                    month_end_action = re.search(r'(\d+)', date)
                    end = helper.get_date_plus_days(int(month_end_action.group(1)) * 30)
            except AttributeError:
                self.queue.put('log error when processing dates')
            desc = div.select_one('.SpecialOfferPreview-description').text.strip()
            if 'промокод' in name.lower():
                try:
                    code = re.search(r'([A-Z0-9]+)', name).group(1)
                except AttributeError:
                    code = 'Не требуется'
            else:
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
