from PyQt5.QtWidgets import QDialog
from design.custom_dialog_resizer import Ui_Dialog as Ui_Dialog_resizer
from design.custom_dialog_parser import Ui_Dialog as Ui_Dialog_parser
from helpers import win32
from parsers.butic import Butic_process
from parsers.process_akusherstvo import Akusherstvo_process
from parsers.process_book import Book_process
from parsers.process_holodilnik import Holodilnik_process
from parsers.process_ildebote import Ildebote_process
from parsers.process_kolesadarom import Kolesadarom_process
from parsers.process_kupivip import Kupivip_process
from parsers.process_sephora import Sephora_process
from parsers.process_utkonos import Utkonos_process
from parsers.process_vseintrumenti import Vseinstrumenti_process
from helpers.start_new_process import StartNewProcess


class CustomDialog_parser(QDialog, Ui_Dialog_parser):
    """Класс для кастомизации диалогового окна"""

    def __init__(self, mainwindow):
        QDialog.__init__(self)
        self.mainwindow = mainwindow
        self.setupUi(self)
        self.ok.clicked.connect(self.change)

    def change(self):
        processes = []
        if self.sephora.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Sephora_process))
        if self.ildebote.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Ildebote_process))
        if self.kupivip.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Kupivip_process))
        if self.akusherstvo.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Akusherstvo_process))
        if self.utkonos.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Utkonos_process))
        if self.vseinstrumenti.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Vseinstrumenti_process))
        if self.butic.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Butic_process))
        if self.book.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Book_process))
        if self.holodilnik.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Holodilnik_process))
        if self.kolesadarom.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Kolesadarom_process))
        [process.start() for process in processes]
        self.mainwindow.change_progress_signal.emit(len(processes))
        self.close()

    def exit_func(self):
        self.close()


class CustomDialog_resizer(QDialog, Ui_Dialog_resizer):
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
