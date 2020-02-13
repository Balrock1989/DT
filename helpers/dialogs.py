from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QDialog
from custom_dialog_resizer import Ui_Dialog as Ui_Dialog_resizer
from custom_dialog_parser import Ui_Dialog as Ui_Dialog_parser
from Parsers.process_akusherstvo import Akusherstvo_process
from Parsers.process_ildebote import Ildebote_process
from Parsers.process_kupivip import Kupivip_process
from Parsers.process_sephora import Sephora_process
from Parsers.process_utkonos import Utkonos_process
from Parsers.process_vseintrumenti import Vseinstrumenti_process
from helpers.start_new_process import StartNewProcess


class CustomDialog_parser(QDialog, Ui_Dialog_parser):
    """Класс для кастомизации диалогового окна"""

    def __init__(self, mainwindow):
        QDialog.__init__(self)
        self.mainwindow = mainwindow
        self.setupUi(self)
        self.ok.clicked.connect(self.change)

    def change(self):
        if self.sephora.isChecked():
            parser = Sephora_process
            sephora_process = StartNewProcess(self.mainwindow, parser)
            sephora_process.start()
        if self.ildebote.isChecked():
            parser = Ildebote_process
            ildebote_process = StartNewProcess(self.mainwindow, parser)
            ildebote_process.start()
        if self.kupivip.isChecked():
            parser = Kupivip_process
            kupivip_process = StartNewProcess(self.mainwindow, parser)
            kupivip_process.start()
        if self.akusherstvo.isChecked():
            parser = Akusherstvo_process
            akusherstvo_process = StartNewProcess(self.mainwindow, parser)
            akusherstvo_process.start()
        if self.utkonos.isChecked():
            parser = Utkonos_process
            utkonos_process = StartNewProcess(self.mainwindow, parser)
            utkonos_process.start()
        if self.vseinstrumenti.isChecked():
            parser = Vseinstrumenti_process
            vseinstrumenti_process = StartNewProcess(self.mainwindow, parser)
            vseinstrumenti_process.start()
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
