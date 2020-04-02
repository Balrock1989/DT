import re
from multiprocessing import Process
from bs4 import BeautifulSoup

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Volt_process(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "220Volt"

    def run(self):
        partner_name = '220Volt'
        actions_data = []
        main_url = 'https://ulyanovsk.220-volt.ru/share/0/'
        page, driver = helper.get_page_use_webdriver(main_url, quit=False)
        divs = page.find_all('div', class_='actionContainer rel')
        for div in divs:
            date = div.find('div', class_='actionPeriod').text.strip()
            start, end = helper.convert_text_date(date)
            name = div.find('div', class_='actionText').h4.text.strip()
            url = 'https://220-volt.ru' + div.find('a', class_='activeButton').get('href')
            driver.get(url)
            action_page = BeautifulSoup(driver.page_source, 'lxml')
            desc_block = action_page.find('div', class_='seoText')
            desc = desc_block.text.strip()
            desc = re.sub(r'\s{2,}', ' ', desc).strip()
            code = 'Не требуется'
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if helper.promotion_is_outdated(end):
                continue
            if not self.ignore:
                if actions_exists_in_db(partner_name, name, start, end):
                    continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        driver.quit()
        helper.filling_queue(self.queue, actions_data, partner_name)
