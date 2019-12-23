import datetime
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir, QThread
from PyQt5.QtWidgets import QFileDialog, QSpinBox, QDialog
from CustomDesign import Ui_MainWindow
from Rename_image import Rename
from WebDriver import Add_banner
from CustomDialog import Ui_Dialog
from image_sizer import Resizer
import GlobalHotKey
import threading


# pyinstaller --onedir --noconsole --add-data "chromedriver.exe;." gui.py

class CustomDialog(QDialog, Ui_Dialog):
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


class ProgressBarThread(QThread):
    def __init__(self, mainwindow):
        super(ProgressBarThread, self).__init__()
        self.mainwindow = mainwindow
        self.width_resize = ''
        self.height_resize = ''

    def run(self):
        self.mainwindow.driver.auth()


class DoubleTrade(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dir_name = ''
        self.sb_num1 = QSpinBox()
        self.thread = ProgressBarThread(mainwindow=self)
        self.driver = Add_banner()
        self.sizer = Resizer()
        self.init_buttons()


    def init_buttons(self):
        now = datetime.datetime.now()
        self.date_start.append(now.strftime("%d.%m.%Y"))
        self.path_buttom.clicked.connect(self.get_path)
        self.rename_button.clicked.connect(self.rename)
        self.run_browser_button.clicked.connect(self.launch_thread)
        self.resize_buttom.clicked.connect(self.resizer)

    def get_path(self):
        self.path_window.clear()
        self.dir_name = os.path.normpath(QFileDialog.getExistingDirectory(
            None,
            "Open Directory",
            QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        ))
        self.path_window.append(self.dir_name)

    def add_banner(self):
        self.driver.exit = False
        self.driver.start_data = self.date_start.toPlainText()
        self.driver.end_data = self.date_end.toPlainText()
        self.driver.url = self.url.toPlainText()
        self.driver.add_banner(self)

    def rename(self):
        self.command_window.clear()
        rename = Rename()
        rename.rename_image(gui=self,
                            path=self.dir_name,
                            end_data=self.date_end.toPlainText(),
                            checkbox=self.rename_checbox.isChecked())

    def resizer(self):
        self.command_window.clear()
        self.sizer.resize_image(gui=self, path=self.dir_name, end_data=self.date_end.toPlainText())

    def launch_thread(self):
        self.command_window.clear()
        self.driver.start_data = self.date_start.toPlainText()
        self.driver.end_data = self.date_end.toPlainText()
        self.driver.url = self.url.toPlainText()
        self.thread.start()

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
    app = QtWidgets.QApplication(sys.argv)
    window = DoubleTrade()
    window.show()
    threading.Thread(target=GlobalHotKey.show, args=(window,), daemon=True).start()
    app.exec_()


if __name__ == '__main__':
    main()
