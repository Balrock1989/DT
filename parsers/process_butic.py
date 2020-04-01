import re
from datetime import datetime
from multiprocessing import Process
import requests
import auth
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Butic_process(Process):
    """Парсер для партнера Бутик"""

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Бутик"

    def run(self):
        partner_name = 'Бутик'
        actions_data = []
        session = requests.Session()
        result = session.post(auth.butic_auth_url, data=auth.butic_payload)
        if result.status_code != 200:
            raise RuntimeError
        result_data = result.json()
        if not result_data.get('token'):
            raise RuntimeError
        bearer_value = 'Bearer ' + result_data['token']
        auth_header = {'Authorization': bearer_value}
        promo_data = {"operationName": "getPromotions",
                      "variables": {"where": {"status": {"$ne": 3}}, "limit": 100,
                                    "order": "reverse:created"},
                      "query": "query getPromotions($limit: Int!, $where: SequelizeJSON, $order: String!) {promotions(limit: $limit, where: $where, order: $order) {\n    rows {\n      id\n      url\n      title\n      status\n      preview\n      description\n      image\n      start\n      end\n      created\n      updated\n      __typename\n    }\n    __typename\n  }\n}"}
        result = session.post(auth.butic_main_url, headers=auth_header, json=promo_data)
        if result.status_code != 200:
            raise RuntimeError
        if len(result.json()['data']['promotions']['rows']) == 0:
            self.queue.put(f'Акции по {partner_name} не найдены ')
            self.queue.put('progress')
            return
        for action in result.json()['data']['promotions']['rows']:
            action_id = int(action['id'])
            name = action['title']
            start = datetime.strptime(action['start'], '%Y-%m-%d').strftime('%d.%m.%Y')
            end = datetime.strptime(action['end'], '%Y-%m-%d').strftime('%d.%m.%Y')

            full_description = action['description']

            try:
                code = re.search(r'([a-zA-Z]+.*)', action['preview']).group(1).strip()
            except Exception:
                code = "Не требуется"
            url_woman = re.search(r'для женщин:.*(https.*)', full_description).group(1).strip()
            url_man = re.search(r'для мужчин:.*(https.*)', full_description).group(1).strip()
            desc = re.search(r'(?s)Подробные условия:(.*)', full_description).group(1).strip()
            desc = re.sub(r'\*', '', desc).strip()
            if helper.promotion_is_outdated(end):
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if actions_exists_in_db(partner_name, name, start, end):
                continue
            action_man = helper.generate_action(partner_name, name, start, end, desc, code, url_man, action_type,
                                                short_desc)
            action_woman = helper.generate_action(partner_name, name, start, end, desc, code, url_woman, action_type,
                                                  short_desc)
            actions_data.append(action_man)
            actions_data.append(action_woman)
            banner_data = {"operationName": "getBanners",
                           "variables": {"where": {"promotionId": action_id}, "limit": 1000},
                           "query": "query getBanners($limit: Int!, $where: JSON) {\n  banners(limit: $limit, where: $where) {\n    rows {\n      id\n      promotionId\n      name\n      path\n      width\n      height\n      __typename\n    }\n    __typename\n  }\n}\n"}
            banner_result = session.post(auth.butic_main_url, headers=auth_header, json=banner_data)
            if banner_result.status_code != 200:
                raise RuntimeError
            begin_url_banner = "https://partners.butik.ru/api/static"
            banner_result = banner_result.json()
            banners_links = []
            for banner in banner_result['data']['banners']['rows']:
                link = begin_url_banner + banner['path']
                banners_links.append(link)
            helper.banner_downloader(banners_links, self.queue)
        helper.filling_queue(self.queue, actions_data, partner_name)
