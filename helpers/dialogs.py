from PyQt5.QtWidgets import QDialog
from design.custom_dialog_resizer import Ui_Dialog as Ui_Dialog_resizer
from design.custom_dialog_parser import Ui_Dialog as Ui_Dialog_parser
from parsers.butic import Butic_process
from parsers.process_akusherstvo import Akusherstvo_process
from parsers.process_ildebote import Ildebote_process
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
        self.count_process = 0

    def change(self):
        if self.sephora.isChecked():
            StartNewProcess(self.mainwindow, Sephora_process).start()
            self.count_process += 1
        if self.ildebote.isChecked():
            StartNewProcess(self.mainwindow, Ildebote_process).start()
            self.count_process += 1
        if self.kupivip.isChecked():
            StartNewProcess(self.mainwindow, Kupivip_process).start()
            self.count_process += 1
        if self.akusherstvo.isChecked():
            StartNewProcess(self.mainwindow, Akusherstvo_process).start()
            self.count_process += 1
        if self.utkonos.isChecked():
            StartNewProcess(self.mainwindow, Utkonos_process).start()
            self.count_process += 1
        if self.vseinstrumenti.isChecked():
            StartNewProcess(self.mainwindow, Vseinstrumenti_process).start()
            self.count_process += 1
        if self.butic.isChecked():
            StartNewProcess(self.mainwindow, Butic_process).start()
            self.count_process += 1
        self.mainwindow.change_progress_signal.emit(self.count_process)
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
