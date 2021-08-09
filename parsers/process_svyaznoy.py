import re
from multiprocessing import Process

from bs4 import BeautifulSoup

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class Svyaznoy_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Связной"

    def run(self):
        partner_name = 'Связной'
        actions_data = []
        main_url = 'https://www.svyaznoy.ru/special-offers'
        page, driver = self.utils.ACTIONS_UTIL.get_page_use_webdriver(main_url, quit=False)
        divs = page.find_all('div', class_='b-article-preview__inner')
        links = []
        for div in divs:
            links.append(div.find('a', class_='b-article-preview__link').get('href'))
        self.queue.put(f'set {len(links)}')
        for link in links:
            driver.get(link)
            page = BeautifulSoup(driver.page_source, 'lxml')
            action = Action(partner_name)
            action.name = page.h1.text
            date = page.find('div', class_='b-event-info__item').find_all('span', class_='b-event-info__date')
            if len(date) == 2:
                action.start = self.utils.DATE_UTIL.get_one_date(date[0].text.strip())
                action.end = self.utils.DATE_UTIL.get_one_date(date[1].text.strip())
            elif len(date) == 1:
                action.start = self.utils.DATE_UTIL.get_one_date(date[0].text.strip())
                action.end = self.utils.DATE_UTIL.get_date_end_month()
            else:
                self.queue.put(f'Не удалось загрузить акцию "{action.name}" из-за даты "{date}"')
            action.url = link
            action.desc = page.find('div', class_='b-article').text.strip()
            action.desc = re.sub(r'\s{2,}', ' ', action.desc).strip()
            action.code = self.utils.ACTIONS_UTIL.find_promo_code(action.desc)
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db_new(action):
                    self.queue.put('progress')
                    continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action_new(action))
            self.queue.put('progress')
        driver.quit()
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, partner_name)
