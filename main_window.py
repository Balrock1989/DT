from datetime import datetime
import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QDir, QThread, QWaitCondition, QMutex, pyqtSignal, pyqtSlot, QObject, Qt
from PyQt5.QtWidgets import QFileDialog, QSpinBox, QDialog
from custom_design import Ui_MainWindow
from rename_image import Rename
from web_driver import WebDriver
from parsers import Parsers
from custom_dialog import Ui_Dialog
from image_sizer import Resizer
import global_hotkey
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
        mainwindow.browser = self.web
        self.web.start_data = self.mainwindow.date_start.toPlainText()
        self.web.end_data = self.mainwindow.date_end.toPlainText()
        self.web.url = self.mainwindow.url.toPlainText()

    def run(self):
        self.web.auth(gui=self.mainwindow)


class GlobalHotKey(QThread):
    """Отдельный поток для работы чата"""

    def __init__(self, mainwindow):
        super(GlobalHotKey, self).__init__()
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
        self.log = logger.log
        self.web_thread = None
        self.sizer = None
        self.web_thread_run = False
        self.parser_thread = ParserThread(mainwindow=self)
        self.ghk = GlobalHotKey(self)
        self.ghk.start()
        self.init_buttons()
        self.init_signals()
        self.try_start_browser = 0
        self.browser = None

    set_partner_name_signal = pyqtSignal(str)
    chat_print_signal = pyqtSignal(str)
    set_exit_signal = pyqtSignal()

    @pyqtSlot(str)
    def set_partner_name_slot(self, text):
        self.partner_name.setText(text)

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

    def init_signals(self):
        self.moveToThread(self.parser_thread)
        self.moveToThread(self.ghk)
        self.set_partner_name_signal.connect(self.set_partner_name_slot)
        self.chat_print_signal.connect(self.chat_print_slot)
        self.set_exit_signal.connect(self.set_exit_slot)

    def init_buttons(self):
        now = datetime.now()
        self.date_start.append(now.strftime('%d.%m.%Y'))
        self.path_buttom.clicked.connect(self.get_path)
        self.rename_button.clicked.connect(self.rename)
        self.run_browser.clicked.connect(self.launch_thread_dt)
        self.resize_buttom.clicked.connect(self.resizer)
        self.parser_button.clicked.connect(self.parsers)

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
                self.chat_print_signal.emit(f'Браузер уже запущен, попытка {self.try_start_browser}')

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


def main():
    logger.configure_logging()
    app = QtWidgets.QApplication(sys.argv)
    window = DT()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
