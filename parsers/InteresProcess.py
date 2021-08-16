from multiprocessing import Process
from time import sleep

from bs4 import BeautifulSoup

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class InteresProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "1С_Интерес"

    def run(self):
        actions_data = []
        page, driver = self.utils.ACTIONS_UTIL.get_page_use_webdriver('https://www.1c-interes.ru/special_actions/',
                                                                      quit=False)
        for i in range(0, 5):
            next_btn = self.utils.ACTIONS_UTIL.check_exists_by_css(driver, '.news-next-btn')
            if next_btn:
                next_btn.click()
                sleep(1)
        page = BeautifulSoup(driver.page_source, 'lxml')
        divs = page.find_all("div", class_='main-holder')
        begin_url = 'https://www.1c-interes.ru'
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            action.url = begin_url + div.a.get('href').strip()
            action.name = div.h2.text.strip()
            try:
                date = div.find('div', class_='preorder-active-to').text.strip()
                action.start, action.end = self.utils.DATE_UTIL.get_do_period(date)
            except AttributeError:
                action.start = self.utils.DATE_UTIL.DATA_NOW
                action.end = self.utils.DATE_UTIL.get_date_end_month()
            action.desc = div.find('div', class_='h2 tile-hide').text.strip()
            action.code = 'Не требуется'
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db_new(action):
                    self.queue.put('progress')
                    continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
