# from datetime import datetime
# from multiprocessing import Process
#
# from database.data_base import actions_exists_in_db_new
# from helpers.Utils import Utils
# from models.action import Action
#
#
# class EldoradoProcess(Process):
#
#     def __init__(self, queue, ignore):
#         super().__init__()
#         self.queue = queue.queue
#         self.ignore = ignore
#         self.utils = Utils(self.queue)
#
#     def __str__(self):
#         return "Эльдорадо"
#
#     def run(self):
#         partner_name = 'Эльдорадо'
#         actions_data = []
#         base_url = 'https://www.eldorado.ru'
#         main_url = 'https://www.eldorado.ru/actions.php?type=online'
#         page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
#         divs = page.find_all('a', class_='promotion__promotion')
#         self.queue.put(f'set {len(divs)}')
#         for div in divs:
#             action = Action(str(self))
#             try:
#                 action.url = str(div.get('href'))
#                 action.url = div.get('href') if 'www' in action.url else base_url + div.get('href')
#             except TypeError:
#                 self.queue.put('progress')
#                 continue
#             action.name = div.find('div', class_='promotion__promotion-title').text.strip()
#             action.start = self.utils.DATE_UTIL.DATA_NOW
#             try:
#                 action.end = div.find('div', class_='promotion__promotion-date').get('data-date')
#                 action.end = datetime.strptime(action.end, '%Y-%m-%d').strftime('%d.%m.%Y')
#             except ValueError:
#                 self.queue.put('progress')
#                 continue
#             action.code = "Не требуется"
#             action.desc = action.name
#             action.short_desc = ''
#             action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
#             if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
#                 self.queue.put('progress')
#                 continue
#             if not self.ignore:
#                 if actions_exists_in_db_new(action):
#                     self.queue.put('progress')
#                     continue
#             actions_data.append(self.utils.ACTIONS_UTIL.generate_action_new(action))
#             self.queue.put('progress')
#         self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, partner_name)
