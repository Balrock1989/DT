import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Pharmacosmetica_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "ФармКосметика"

    def run(self):
        partner_name = 'ФармКосметика'
        actions_data = []
        base_url = 'https://www.pharmacosmetica.ru'
        links = []
        for i in range(3):
            main_url = f'https://www.pharmacosmetica.ru/podarki-dlya-vas/?page={i}'
            try:
                page = helper.get_page_use_request(main_url)
            except:
                continue
            divs = page.find_all('a', class_='podarok')
            for div in divs:
                links.append(base_url + div.get('href'))
        print(links)
        print(len(links))
        # for link in links:
        #     driver.get(link)
        #     page = BeautifulSoup(driver.page_source, 'lxml')
        #     name = page.h1.text
        #     date = page.find_all('span', class_='b-event-info__date')
        #     start = helper.get_one_date(date[0].text.strip())
        #     end = helper.get_one_date(date[1].text.strip())
        #     url = link
        #     desc = page.find('div', class_='b-article').text.strip()
        #     desc = re.sub(r'\s{2,}', ' ', desc).strip()
        #     code = helper.find_promo_code(desc)
        #     short_desc = ''
        #     action_type = helper.check_action_type(code, name, desc)
        #     if helper.promotion_is_outdated(end):
        #         continue
        #     if not self.ignore:
        #         if actions_exists_in_db(partner_name, name, start, end):
        #             continue
        #     action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
        #     actions_data.append(action)
        # driver.quit()
        # helper.filling_queue(self.queue, actions_data, partner_name)



