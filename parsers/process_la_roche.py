from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class La_roche_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "La Roche posay"

    def run(self):
        partner_name = 'La Roche posay'
        actions_data = []
        base_url = 'https://www.laroche-posay.ru/'
        main_url = base_url + 'special-offers/'
        page = helper.get_page_use_request(main_url)
        divs = page.find('table', class_='promo').findAll('tr')
        for div in divs[1:]:
            url = base_url + div.find('a').get('href')
            name = div.findAll('td')[0].text.strip() + '. ' + div.findAll('td')[1].text.strip()
            start = helper.get_first_day_month()
            end = helper.get_date_end_month()
            promo_text = div.findAll('td')[2].text.strip()
            code = promo_text if promo_text != 'ИСПОЛЬЗОВАТЬ' else 'Не требуется'
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
