import os
import sys
from multiprocessing import freeze_support
# pip install PyQt5
# pip install pillow
# pip install pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
# pip install pyinstaller-hooks
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QDir, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog

import WebDriver
from database.DataBase import create_database, print_stat, delete_expired_actions
from helpers.MyQueue import MyQueue
from design.UiMainWindow import UiMainWindow
from helpers.Utils import Utils
from helpers.CustomDialogParser import CustomDialogResizer, CustomDialogParser
from RenameImage import RenameImage
from ImageSizer import ImageSizer
from helpers import GlobalHotKey, Logger

# pyinstaller --onedir --noconsole --add-data "chromedriver.exe;." --add-data "icon.png;." MainWindow.py
# pyinstaller mainwindow.spec --noconfirm
sys.excepthook = Utils().exception_hook


class DT(QtWidgets.QMainWindow, UiMainWindow):
    """Основной поток для работы интерфейса"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dir_name = ''
        self.log = Logger.log
        self.web_thread = None
        self.sizer = None
        self.ghk = GlobalHotKey.GlobalHotKey(self)
        self.ghk.start()
        self.try_start_browser = 0
        self.browser = None
        self.queue = MyQueue(self)
        self.queue.start()
        self.utils = Utils(self.queue)
        self.init_buttons()
        self.init_signals()


    set_partner_name_signal = pyqtSignal(str)
    chat_print_signal = pyqtSignal(str)
    del_partner_name_signal = pyqtSignal(str)
    set_exit_signal = pyqtSignal()
    change_progress_signal = pyqtSignal(int)
    reset_progress_signal = pyqtSignal()

    @pyqtSlot(str)
    def set_partner_name_slot(self, text):
        """Слот для смены имени партнера в селекте(во время парсинга)"""
        self.partner_name.addItem(text)
        self.partner_name.setCurrentText(text)

    @pyqtSlot(str)
    def del_partner_name_slot(self, text):
        """Слот для удаления имени партнера в селекте(после добавления акций)"""
        index_items = self.partner_name.findText(text)
        self.partner_name.removeItem(index_items)

    @pyqtSlot(str)
    def chat_print_slot(self, text):
        """Слот для вывода информации на экран"""
        self.command_window.append('\n' + text)
        self.command_window.moveCursor(QtGui.QTextCursor.End)
        self.log.info(text)

    @pyqtSlot()
    def set_exit_slot(self):
        """Слот для прерывания процесса кнопкой ESC"""
        if self.web_thread:
            self.web_thread.web.exit = True
        if self.sizer:
            self.sizer.exit = True
        self.reset_progress_signal.emit()

    @pyqtSlot(int)
    def change_progress_slot(self, max_value):
        """Слот для изменения прогресс бара"""

        if max_value:
            self.progress_bar.setMaximum(max_value)
            self.progress_bar.setValue(0)
        else:
            value = self.progress_bar.value() + 1
            self.progress_bar.setValue(value)
        if self.progress_bar.value() == self.progress_bar.maximum():
            self.reset_progress_signal.emit()


    @pyqtSlot()
    def reset_progress_slot(self):
        """Слот для сброса прогресс бара"""
        self.progress_bar.reset()

    def init_signals(self):
        """Инициализация слотов для сигналов"""
        self.set_partner_name_signal.connect(self.set_partner_name_slot)
        self.set_partner_name_signal.emit('actions.csv')
        self.del_partner_name_signal.connect(self.del_partner_name_slot)
        self.chat_print_signal.connect(self.chat_print_slot)
        self.set_exit_signal.connect(self.set_exit_slot)
        self.change_progress_signal.connect(self.change_progress_slot)
        self.reset_progress_signal.connect(self.reset_progress_slot)
        print_stat(self.queue.queue)
        delete_expired_actions(self.queue.queue)


    def init_buttons(self):
        """Инициализация кнопок интерфейса"""
        self.utils.CSV_UTIL.generate_csv()
        self.date_start.append(self.utils.DATE_UTIL.DATA_NOW)
        self.path_buttom.clicked.connect(self.get_path)
        self.rename_button.clicked.connect(self.rename)
        self.run_browser.clicked.connect(self.launch_thread_dt)
        self.resize_buttom.clicked.connect(self.resizer)
        self.parser_button.clicked.connect(self.show_parser_checklist)

    def get_path(self):
        """Выбор пути для работы с файлами"""
        self.path_window.clear()
        self.dir_name = os.path.normpath(QFileDialog.getExistingDirectory(
            None,
            'Open Directory',
            QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        ))
        self.path_window.append(self.dir_name)

    def rename(self):
        """Вызов функции для переименовывания баннеров"""
        rename = RenameImage()
        rename.rename_image(gui=self,
                            end_data=self.date_end.toPlainText(),
                            checkbox=self.rename_checbox.isChecked())

    def resizer(self):
        """Вызов функции для изменения размера баннеров"""
        self.sizer = ImageSizer()
        self.sizer.exit = False
        self.sizer.resize_image(gui=self, end_data=self.date_end.toPlainText())

    def launch_thread_dt(self):
        """Запуск потока для браузера"""
        # win32.close_all_chromedriver()
        if self.web_thread is None:
            self.web_thread = WebDriver.WebThread(mainwindow=self)
            self.web_thread.start()
        else:
            self.try_start_browser += 1
            if self.try_start_browser >= 3:
                self.web_thread = None
                try:
                    self.browser.driver.quit()
                except Exception as exc:
                    self.chat_print_signal.emit(f'Неизвестная ошибка {exc}')
                self.chat_print_signal.emit('Теперь браузер можно запускать')
                self.try_start_browser = 0
            else:
                self.chat_print_signal.emit(f'Браузер уже запущен, попытка {self.try_start_browser}, на 3 он закроется')

    def show_dialog_width(self):
        """Открытие диалога для смены размера по высоте"""
        dialog = CustomDialogResizer(self.sizer, message=f'{self.sizer.count}Введите ШИРИНУ:',
                                     size=f'{self.sizer.w} x {self.sizer.h}')
        dialog.show()
        dialog.exec_()

    def show_dialog_heigth(self):
        """Открытие диалога для смены размера по ширине"""
        dialog = CustomDialogResizer(self.sizer, message=f'{self.sizer.count}Введите ВЫСОТУ:',
                                     size=f'{self.sizer.w} x {self.sizer.h}')
        dialog.show()
        dialog.exec_()

    def show_parser_checklist(self):
        """Открытие диалога для выбора парсеров"""
        dialog = CustomDialogParser(self)
        dialog.show()
        dialog.exec_()


def main():
    # win32.close_all_chromedriver()
    Logger.configure_logging()
    create_database()
    app = QtWidgets.QApplication(sys.argv)
    window = DT()
    window.show()
    app.exec_()


if __name__ == '__main__':
    """Без freeze_support дублируются процессы"""
    freeze_support()
    main()
    # win32.close_all_chromedriver()
