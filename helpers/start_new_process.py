from threading import Thread


class StartNewProcess(Thread):
    """Отдельный поток для запуска новых процессов"""

    def __init__(self, mainwindow, process):
        super(StartNewProcess, self).__init__()
        self.mainwindow = mainwindow
        self.queue = mainwindow.queue
        self.process = process

    def run(self):
        self.process = self.process(self.queue, self.mainwindow.ignore_database.isChecked())
        self.mainwindow.chat_print_signal.emit(f'Запущен процесс: {self.process}')
        self.process.daemon = True
        self.process.start()


