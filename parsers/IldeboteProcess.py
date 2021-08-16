# import threading
# from datetime import datetime, timedelta
# from multiprocessing import Process
#
# from database.data_base import actions_exists_in_db_new
# from helpers.Utils import Utils
# from models.action import Action
#
#
# class IldeboteProcess(Process):
#     def __init__(self, queue, ignore):
#         super().__init__()
#         self.queue = queue.queue
#         self.ignore = ignore
#         self.utils = Utils(self.queue)
#
#     def __str__(self):
#         return "ИльДэБотэ"
#
#     def run(self):
#         actions_data = []
#         lock = threading.Lock()
#         url = 'https://iledebeaute.ru/company/actions'
#         page = self.utils.ACTIONS_UTIL.get_page_use_request(url)
#         divs = page.find_all("div", class_='news_block')
#         self.queue.put(f'set {len(divs)}')
#         for div in divs:
#             action = Action(str(self))
#             action.name = div.h2.text
#             try:
#                 action.start = self.utils.DATE_UTIL.get_start_date_in_date(div.find("p", class_='date').text.strip(),
#                                                                            False)
#             except AttributeError:
#                 action.start = self.utils.DATE_UTIL.DATA_NOW
#             action.end = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
#             action.desc = div.find("p", class_='desc').text.strip()
#             action.code = 'Не требуется'
#             if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
#                 self.queue.put('progress')
#                 continue
#             action.short_desc = ''
#             action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
#             if not self.ignore:
#                 with lock:
#                     if actions_exists_in_db_new(action):
#                         self.queue.put('progress')
#                         continue
#             actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
#             self.queue.put('progress')
#         self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
