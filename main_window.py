from datetime import datetime
import os
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QDir, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QSpinBox
from helpers.my_queue import MyQueue
from custom_design import Ui_MainWindow
from helpers.dialogs import CustomDialog_resizer, CustomDialog_parser
from rename_image import Rename
from web_driver import WebDriver
from image_sizer import Resizer
import global_hotkey
import logger
import helpers.helper as helper

# pyinstaller --onedir --noconsole --add-data "chromedriver.exe;." --add-data "icon.png;." main_window.py
# pyinstaller --onedir --noconsole --add-data "chromedriver.exe;." --add-data "icon.png;." --additional-hooks-dir=helpers main_window.py
# pyinstaller main_window.spec



sys.excepthook = helper.exception_hook

class WebThread(QThread):
    """Отдельный поток для работы браузера"""

    def __init__(self, mainwindow):
        super(WebThread, self).__init__()
        self.mainwindow = mainwindow
        self.web = WebDriver(mainwindow)
        mainwindow.browser = self.web
        self.web.start_data = self.mainwindow.date_start.toPlainText()
        self.web.end_data = self.mainwindow.date_end.toPlainText()
        self.web.url = self.mainwindow.url.toPlainText()

    def run(self):
        self.web.auth()


class GlobalHotKey(QThread):
    """Отдельный поток для работы чата"""

    def __init__(self, mainwindow):
        super(GlobalHotKey, self).__init__()
        self.mainwindow = mainwindow

    def run(self):
        global_hotkey.hotkey(self.mainwindow)



class DT(QtWidgets.QMainWindow, Ui_MainWindow):
    """Основной поток интерфейса"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dir_name = ''
        self.sb_num1 = QSpinBox()
        self.log = logger.log
        self.web_thread = None
        self.sizer = None
        self.web_thread_run = False
        self.ghk = GlobalHotKey(self)
        self.ghk.start()
        self.try_start_browser = 0
        self.browser = None
        self.queue = MyQueue(self)
        self.queue.start()
        self.init_buttons()
        self.init_signals()

    set_partner_name_signal = pyqtSignal(str)
    chat_print_signal = pyqtSignal(str)
    del_partner_name_signal = pyqtSignal(str)
    set_exit_signal = pyqtSignal()
    # change_progress_signal = pyqtSignal(int, int)
    # reset_progress_signal = pyqtSignal()

    @pyqtSlot(str)
    def set_partner_name_slot(self, text):
        self.partner_name.addItem(text)
        self.partner_name.setCurrentText(text)

    @pyqtSlot(str)
    def del_partner_name_slot(self, text):
        index_items = self.partner_name.findText(text)
        self.partner_name.removeItem(index_items)

    @pyqtSlot(str)
    def chat_print_slot(self, text):
        """Функция для вывода информации на экран. Активировать окно и добавить вывод через очередь"""
        self.command_window.append('\n' + text)
        self.command_window.moveCursor(QtGui.QTextCursor.End)
        self.log.info(text)

    @pyqtSlot()
    def set_exit_slot(self):
        if self.web_thread:
            self.web_thread.web.exit = True
        if self.sizer:
            self.sizer.exit = True

    # @pyqtSlot(int, int)
    # def change_progress_slot(self, value, max):
    #     self.progress.setMaximum(max)
    #     self.progress.setValue(value)
    #
    # def change_progress(self, value, max):
    #     self.queue.queue.put(self.change_progress_signal.emit(value, max))
    #
    # @pyqtSlot()
    # def reset_progress_slot(self):
    #     self.progress.reset()

    def init_signals(self):
        self.moveToThread(self.queue)
        self.moveToThread(self.ghk)
        self.set_partner_name_signal.connect(self.set_partner_name_slot)
        self.del_partner_name_signal.connect(self.del_partner_name_slot)
        self.chat_print_signal.connect(self.chat_print_slot)
        self.set_exit_signal.connect(self.set_exit_slot)
        # self.change_progress_signal.connect(self.change_progress_slot)
        # self.reset_progress_signal.connect(self.reset_progress_slot)

    def init_buttons(self):
        now = datetime.now()
        helper.generate_csv()
        self.date_start.append(now.strftime('%d.%m.%Y'))
        self.path_buttom.clicked.connect(self.get_path)
        self.rename_button.clicked.connect(self.rename)
        self.run_browser.clicked.connect(self.launch_thread_dt)
        self.resize_buttom.clicked.connect(self.resizer)
        self.parser_button.clicked.connect(self.show_parser_checklist)

    # def keyPressEvent(self, e):
    #     if e.key() == Qt.Key_Escape:
    #         if self.web_thread:
    #             self.web_thread.web.exit = True

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


    def launch_thread_dt(self):
        if self.web_thread is None:
            self.web_thread = WebThread(mainwindow=self)
            self.moveToThread(self.web_thread)
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
        dialog = CustomDialog_resizer(self.sizer, message=f'{self.sizer.count}Введите ШИРИНУ:',
                                      size=f'{self.sizer.w} x {self.sizer.h}')
        dialog.show()
        dialog.exec_()

    def show_dialog_heigth(self):
        dialog = CustomDialog_resizer(self.sizer, message=f'{self.sizer.count}Введите ВЫСОТУ:',
                                      size=f'{self.sizer.w} x {self.sizer.h}')
        dialog.show()
        dialog.exec_()

    def show_parser_checklist(self):
        dialog = CustomDialog_parser(self)
        self.moveToThread(dialog)
        dialog.show()
        dialog.exec_()


def main():
    logger.configure_logging()
    app = QtWidgets.QApplication(sys.argv)
    window = DT()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
