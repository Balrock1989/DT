from threading import Thread


class StartNewProcess(Thread):
    """Отдельный поток для работы чата"""

    def __init__(self, mainwindow, parser):
        super(StartNewProcess, self).__init__()
        self.mainwindow = mainwindow
        self.queue = mainwindow.queue.queue
        self.parser = parser

    def run(self):
        self.parser = self.parser(self.queue)
        self.mainwindow.chat_print_signal.emit(f'Началась загрузка {self.parser}')
        self.parser.daemon = False
        self.parser.start()
        # self.parser.join()

