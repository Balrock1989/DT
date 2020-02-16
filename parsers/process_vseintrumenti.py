import re
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import helpers.helper as helper


class Vseinstrumenti_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "ВсеИнструменты"

    def run(self):
        partner = 'Все инструменты'
        actions_data = []
        options = Options()
        options.add_argument('--disable-gpu')
        # TODO разобраться почему перестал работать headless
        main_url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
        driver = webdriver.Chrome(options=options)
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        divs = page.find_all("div", class_='action_main')
        for div in divs:
            name = div.find('div', class_='action_header').a.text.strip()
            code = 'Не требуется'
            action_type = 'скидка'
            url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
            desc = div.find('div', class_='act_descr').find_all('p')[3].text.strip()
            incoming_date = div.find('div', class_='act_descr').find_all('p')[0].text.strip()
            incoming_date = re.search(r'(\d.*)\–\s(.*)', incoming_date.lower())
            try:
                start, end = helper.get_double_date(incoming_date.group(1), incoming_date.group(2))
            except Exception:
                start, end = helper.get_date_now_to_end_month()
            action = helper.generate_action(partner, name, start, end, desc, code, url, action_type)
            actions_data.append(action)

        self.queue.put(actions_data)
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put((partner,))
        self.queue.put('progress')
