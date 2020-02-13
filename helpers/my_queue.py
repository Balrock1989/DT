from multiprocessing import Queue

from PyQt5.QtCore import QThread


class MyQueue(QThread):
    """Отдельный поток для работы очереди"""

    def __init__(self, mainwindow):
        super(MyQueue, self).__init__()
        self.mainwindow = mainwindow
        self.queue = Queue()

    def run(self):
        while True:
            income_data = self.queue.get()
            if isinstance(income_data, list):
                partner_name = income_data[0]["Имя партнера"]
                for n, a in enumerate(income_data, 1):
                    self.mainwindow.chat_print_signal.emit((f'---№{n}\n'))
                    action = ''
                    for key, value in a.items():
                        action = action + "".join('{:_<20}: {}\n'.format(key, value))
                    self.mainwindow.chat_print_signal.emit(action)
                self.mainwindow.chat_print_signal.emit('*' * 60)
                self.mainwindow.chat_print_signal.emit(
                    f'Имя партнера: {partner_name}, загружено акций: {len(income_data)}')
                self.mainwindow.chat_print_signal.emit('*' * 60)
            elif callable(income_data):
                self.queue.get()
            elif isinstance(income_data, tuple):
                self.mainwindow.set_partner_name_signal.emit(income_data[0])
            elif isinstance(income_data, str):
                if 'progress' in income_data:
                    self.mainwindow.change_progress_signal.emit(0)
                    if self.mainwindow.progress_bar.value() == self.mainwindow.progress_bar.maximum() - 1:
                        self.mainwindow.reset_progress_signal.emit()
                    continue
                if income_data:
                    self.mainwindow.chat_print_signal.emit(income_data)
            else:
                pass

