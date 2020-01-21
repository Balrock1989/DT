from datetime import datetime
import os
import sys
from queue import Queue
import pyautogui
import win32con
import win32gui
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QDir, QThread
from PyQt5.QtWidgets import QFileDialog, QSpinBox, QDialog
from custom_design import Ui_MainWindow
from rename_image import Rename
from web_driver import WebDriver
from parsers import Parsers
from custom_dialog import Ui_Dialog
from image_sizer import Resizer
import global_hotkey
import threading
import logger



# pyinstaller --onedir --noconsole --add-data "chromedriver.exe;." main_window.py

class CustomDialog(QDialog, Ui_Dialog):
    """Класс для кастомизации диалогового окна"""

    def __init__(self, sizer, message, size):
        QDialog.__init__(self)
        self.sizer = sizer
        self.setupUi(self)
        self.ok.clicked.connect(self.change)
        self.textEdit.returnPressed.connect(self.ok.click)
        self.label.setText(message)
        self.label2.setText(size)

    def change(self):
        if not self.textEdit.text():
            self.sizer.basewidth = self.sizer.w
            self.sizer.baseheight = self.sizer.h
        else:
            self.sizer.basewidth = int(self.textEdit.text())
            self.sizer.baseheight = int(self.textEdit.text())
        self.close()

    def exit_func(self):
        self.sizer.exit = True
        self.close()


class WebThread(QThread):
    """Отдельный поток для работы браузера"""

    def __init__(self, mainwindow):
        super(WebThread, self).__init__()
        self.mainwindow = mainwindow
        self.web = WebDriver()
        self.web.start_data = self.mainwindow.date_start.toPlainText()
        self.web.end_data = self.mainwindow.date_end.toPlainText()
        self.web.url = self.mainwindow.url.toPlainText()

    def run(self):
        self.web.auth(gui=self.mainwindow)


class ChatThread(QThread):
    """Отдельный поток для работы чата"""

    def __init__(self, mainwindow):
        super(ChatThread, self).__init__()
        self.mainwindow = mainwindow
        self.width_resize = ''
        self.height_resize = ''
        self.queue = Queue()

    def run(self):
        while True:
            self.queue.get()


class ParserThread(QThread):
    """Отдельный поток для работы чата"""

    def __init__(self, mainwindow):
        super(ParserThread, self).__init__()
        self.mainwindow = mainwindow
        self.parser = Parsers()

    def run(self):
        self.parser.parser_sephora(gui=self.mainwindow)


class DT(QtWidgets.QMainWindow, Ui_MainWindow):
    """Основной поток интерфейса"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dir_name = ''
        self.sb_num1 = QSpinBox()
        self.web_thread = None
        self.chat = ChatThread(mainwindow=self)
        self.parser_thread = None
        self.chat.start()
        self.sizer = None
        self.init_buttons()
        self.log = logger.log

    def init_buttons(self):
        now = datetime.now()
        self.date_start.append(now.strftime('%d.%m.%Y'))
        self.path_buttom.clicked.connect(self.get_path)
        self.rename_button.clicked.connect(self.rename)
        self.run_browser.clicked.connect(self.launch_thread_dt)
        self.resize_buttom.clicked.connect(self.resizer)
        self.parser_button.clicked.connect(self.parsers)

    def get_path(self):
        self.path_window.clear()
        self.dir_name = os.path.normpath(QFileDialog.getExistingDirectory(
            None,
            'Open Directory',
            QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        ))
        self.path_window.append(self.dir_name)

    def rename(self):
        rename = Rename()
        rename.rename_image(gui=self,
                            path=self.dir_name,
                            end_data=self.date_end.toPlainText(),
                            checkbox=self.rename_checbox.isChecked())

    def resizer(self):
        self.sizer = Resizer()
        self.sizer.exit = False
        self.sizer.resize_image(gui=self, path=self.dir_name, end_data=self.date_end.toPlainText())

    def parsers(self):
        self.parser_thread = ParserThread(mainwindow=self)
        self.parser_thread.start()

    def launch_thread_dt(self):
        self.web_thread = WebThread(mainwindow=self)
        self.web_thread.start()

    def show_dialog_width(self):
        dialog = CustomDialog(self.sizer, message=f'{self.sizer.count}Введите ШИРИНУ:',
                              size=f'{self.sizer.w} x {self.sizer.h}')
        dialog.show()
        dialog.exec_()

    def show_dialog_heigth(self):
        dialog = CustomDialog(self.sizer, message=f'{self.sizer.count}Введите ВЫСОТУ:',
                              size=f'{self.sizer.w} x {self.sizer.h}')
        dialog.show()
        dialog.exec_()

    def show_process(self):
        """Поиск окна программы в Windows, отображение его и активация, используется для чата"""
        toplist = []
        winlist = []

        def enum_callback(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        try:
            win32gui.EnumWindows(enum_callback, toplist)
            dt_process = [(hwnd, title) for hwnd, title in winlist if 'DTMainWindow' in title]
            dt_process = dt_process[0]
            win32gui.ShowWindow(dt_process[0], win32con.SW_NORMAL)
            pyautogui.press('alt')
            win32gui.SetForegroundWindow(dt_process[0])
            self.command_window.moveCursor(QtGui.QTextCursor.End)
        except Exception:
            self.log.exception(f'Произошла неизвестная ошибка')

    def chat_print(self, text):
        """Функция для вывода информации на экран. Активировать окно и добавить вывод через очередь"""
        self.show_process()
        self.chat.queue.put(self.command_window.append(text))
        self.command_window.moveCursor(QtGui.QTextCursor.End)


def main():
    logger.configure_logging()
    app = QtWidgets.QApplication(sys.argv)
    window = DT()
    window.show()
    threading.Thread(target=global_hotkey.hotkey, args=(window,), daemon=True).start()
    app.exec_()


if __name__ == '__main__':
    main()
