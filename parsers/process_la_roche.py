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
        base_url = 'https://www.laroche-posay.ru'
        main_url = 'https://www.laroche-posay.ru/special-offers/'
        page = helper.get_page_use_request(main_url)
        divs1 = page.findAll('div', class_='special-offers-banner')
        divs1 = divs1
        for div in divs1:
            url = main_url
            text = div.findAll('div', class_='special-offers-banner__text')
            name = text[0].text.strip()
            try:
                date = text[1].text.strip()
                start, end = helper.convert_list_to_date(helper.get_range_date(date))
            except Exception:
                start, end = helper.get_date_now_to_end_month()
            try:
                code = div.find('div', class_='special-offers-banner__code').text.strip()
            except Exception:
                code = 'Не требуется'
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

        divs2 = page.findAll('div', class_='special-offers-promo__content')
        for div in divs2:
            url = base_url + div.find('a').get('href')
            name = div.find(class_='special-offers-promo__text').text.strip()
            start = helper.DATA_NOW
            end = helper.get_date_end_month()
            code = 'Не требуется'
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
