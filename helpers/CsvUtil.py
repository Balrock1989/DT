import csv
import os

from helpers.Paths import HOME_PATH

"""Заголовки для CSV"""


class CsvUtil:
    HEADERS = ['Тип купона', 'Название акции', 'Дата начала', 'Дата окончания', 'Условия акции', 'Купон', 'URL', 'Имя партнера', 'Короткое описание']

    def __init__(self):
        self.actions_csv_path = os.path.join('C:\\', HOME_PATH, 'Desktop', "actions.csv")
        self.actions_csv_path = os.path.normpath(self.actions_csv_path)

    def generate_csv(self):
        """Создает пустой CSV на рабочем столе при запуске программы, для хранения акций"""
        with open(self.actions_csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(self.HEADERS)

    def generate_temp_csv(self):
        """Создает временный CSV, используется для удаления добавленных акций"""
        with open("actions_temp.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(self.HEADERS)

    def write_csv(self, actions):
        """Принимает список из акций, и записывает их в CSV"""
        for action in actions:
            with open(self.actions_csv_path, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.HEADERS, delimiter=";")
                writer.writerow(action)

    def get_count_suitable_actions(self, gui):
        """Возвращает количество акций из списка CSV имя которых выбрано в селекте"""
        with open(self.actions_csv_path, 'r', encoding='utf-8', newline='') as csv_file:
            csv_data = csv.DictReader(csv_file, delimiter=';')
            suitable_actions = [action for action in csv_data if
                                action['Имя партнера'] == gui.partner_name.currentText()]
        return len(suitable_actions)

    def filling_queue(self, queue, actions_data, partner_name):
        queue.put('progress')
        if len(actions_data) == 0:
            queue.put(f'Акции по {partner_name} не найдены ')
            return
        queue.put(actions_data)
        queue.put(self.write_csv(actions_data))
        queue.put((partner_name,))
