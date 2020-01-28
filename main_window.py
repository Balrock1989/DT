from datetime import datetime
import os
import sys
from queue import Queue
from time import sleep

import pyautogui
import win32con
import win32gui
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QDir, QThread, QWaitCondition, QMutex, pyqtSignal, pyqtSlot, QObject
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


class global_hot_key(QThread):
    """Отдельный поток для работы чата"""

    def __init__(self, mainwindow):
        super(global_hot_key, self).__init__()
        self.mainwindow = mainwindow

    def run(self):
        global_hotkey.hotkey(self.mainwindow)


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
        self.parser_thread = ParserThread(mainwindow=self)
        self.chat.start()
        self.sizer = None
        self.init_buttons()
        self.log = logger.log
        self.chromedriver_process = None
        self.dt_process = None
        self.ghk = global_hot_key(self)
        self.ghk.start()
        self.moveToThread(self.ghk)
        self.set_partner_name_signal.connect(self.set_partner_name)
        self.moveToThread(self.ghk)

    set_partner_name_signal = pyqtSignal(str)

    def set_partner_name(self, text):
        print('clear_partner_name', threading.get_ident(), text)
        self.partner_name.setText(text)

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
        self.partner_name.setText('')
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
        self.parser_thread.start()

    def launch_thread_dt(self):
        self.web_thread = WebThread(mainwindow=self)
        self.moveToThread(self.web_thread)
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

        win32gui.EnumWindows(enum_callback, toplist)
        if self.dt_process is None or self.chromedriver_process is None:
            for hwnd, title in winlist:
                if 'DTMainWindow' in title:
                    self.dt_process = hwnd
                if 'chromedriver' in title:
                    self.chromedriver_process = hwnd
        win32gui.ShowWindow(self.dt_process, win32con.SW_NORMAL)
        pyautogui.press('alt')
        win32gui.SetForegroundWindow(self.dt_process)
        self.command_window.moveCursor(QtGui.QTextCursor.End)

    def hide_chrome_console(self):
        self.show_process()
        if self.chromedriver_process:
            win32gui.ShowWindow(self.chromedriver_process, win32con.SW_HIDE)

    def chat_print(self, text):
        """Функция для вывода информации на экран. Активировать окно и добавить вывод через очередь"""
        self.show_process()
        self.chat.queue.put(self.command_window.append(text))
        self.command_window.moveCursor(QtGui.QTextCursor.End)


def main():
    logger.configure_logging()
    app = QtWidgets.QApplication(sys.argv)
    print('main', threading.get_ident())
    window = DT()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
