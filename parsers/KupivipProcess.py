# import re
# import threading
# from datetime import datetime
# from multiprocessing import Process
# import requests
# from bs4 import BeautifulSoup
# import helpers.helper as helper
# from database.data_base import actions_exists_in_db
#
#
# class Kupivip_process(Process):
#     def __init__(self, queue, ignore):
#         super().__init__()
#         self.queue = queue.queue
#         self.ignore = ignore
#
#     def __str__(self):
#         return "КупиВип"
#
#     def run(self):
#         actions_data = []
#         partner_name = 'КупиВип'
#         lock = threading.Lock()
#         page = helper.get_page_use_request('https://www.kupivip.ru/campaigns?showIn=FEMALE&filter=ALL')
#         divs = page.find_all("div", attrs={'data-banner': 'campaign'})
#         self.queue.put(f'set {len(divs)}')
#         # Акции дня
#         for div in divs:
#             percent_actions = ''
#             desc = ''
#             try:
#                 name = div.find("div", class_='brands').text.strip()
#             except:
#                 self.queue.put("Пропущена одна акция без названия")
#                 self.queue.put('progress')
#                 continue
#             try:
#                 percent_actions = div.find("div", class_='percent').text.strip()
#             except Exception:
#                 pass
#             try:
#                 desc = div.find("div", class_='name').text.strip()
#             except Exception:
#                 pass
#             if percent_actions:
#                 name += f'. Скидки до {percent_actions}%'
#             start = datetime.now().strftime('%d.%m.%Y')
#             end = datetime.now().strftime('%d.%m.%Y')
#             code = 'Не требуется'
#             if 'промокод' in name.lower():
#                 code = re.search(r'код\s(.*)\s?', name).group(1)
#             url = 'https://www.kupivip.ru/'
#             if helper.promotion_is_outdated(end):
#                 self.queue.put('progress')
#                 continue
#             short_desc = ''
#             action_type = helper.check_action_type(code, name, desc)
#             if not self.ignore:
#                 with lock:
#                     if actions_exists_in_db(partner_name, name, start, end):
#                         self.queue.put('progress')
#                         continue
#             action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
#             actions_data.append(action)
#             self.queue.put('progress')
#         # Акции с баннера на главной старнице
#         s = requests.Session()
#         s.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
#             "Cookie": "showIn=FEMALE;",
#         })
#         request = s.get("https://www.kupivip.ru/", verify=False)
#         page = BeautifulSoup(request.text, 'lxml')
#         divs = page.find_all('div', class_="banner-primary")
#         self.queue.put(f'set {len(divs)}')
#         for div in divs:
#             name = div.get("data-id")
#             try:
#                 percent = div.find('div', class_="discount").text.strip()
#             except:
#                 percent = ""
#             try:
#                 title = div.find('div', class_="title").text.strip()
#             except:
#                 title = ""
#             try:
#                 desc = div.find('div', class_="text").text.strip()
#             except:
#                 desc = ""
#             if title == name:
#                 title = ''
#             if percent:
#                 name += f'. Скидки до {percent}'
#             start = datetime.now().strftime('%d.%m.%Y')
#             end = datetime.now().strftime('%d.%m.%Y')
#             code = 'Не требуется'
#             desc = title + ' ' + desc
#             url = "https://www.kupivip.ru/" + div.find('a').get("href")
#             if helper.promotion_is_outdated(end):
#                 self.queue.put('progress')
#                 continue
#             short_desc = ''
#             action_type = helper.check_action_type(code, name, desc)
#             if not self.ignore:
#                 with lock:
#                     if actions_exists_in_db(partner_name, name, start, end):
#                         self.queue.put('progress')
#                         continue
#             action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
#             actions_data.append(action)
#             self.queue.put('progress')
#         helper.filling_queue(self.queue, actions_data, partner_name)
