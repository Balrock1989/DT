from PyQt5.QtWidgets import QDialog
from design.custom_dialog_resizer import Ui_Dialog as Ui_Dialog_resizer
from design.custom_dialog_parser import Ui_Dialog as Ui_Dialog_parser
from parsers.process_bethoven import Bethoven_process
from parsers.process_butic import Butic_process
from parsers.process_akusherstvo import Akusherstvo_process
from parsers.process_book import Book_process
from parsers.process_eldorado import Eldorado_process
from parsers.process_holodilnik import Holodilnik_process
from parsers.process_ildebote import Ildebote_process
from parsers.process_kolesadarom import Kolesadarom_process
from parsers.process_kupivip import Kupivip_process
from parsers.process_la_roche import La_roche_process
from parsers.process_mts import Mts_process
from parsers.process_pharmacosmetica import Pharmacosmetica_process
from parsers.process_respublica import Respublica_process
from parsers.process_rivegauche import Rivegauche_process
from parsers.process_rozetka import Rozetka_process
from parsers.process_sephora import Sephora_process
from parsers.process_svyaznoy import Svyaznoy_process
from parsers.process_utkonos import Utkonos_process
from parsers.process_vseintrumenti import Vseinstrumenti_process
from helpers.start_new_process import StartNewProcess
from parsers.process_volt import Volt_process


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
        if self.volt.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Volt_process))
        if self.respublica.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Respublica_process))
        if self.svyaznoy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Svyaznoy_process))
        if self.pharmacosmetica.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Pharmacosmetica_process))
        if self.mts.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Mts_process))
        if self.rivegauche.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Rivegauche_process))
        if self.la_roche.isChecked():
            processes.append(StartNewProcess(self.mainwindow, La_roche_process))
        if self.rozetka.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Rozetka_process))
        if self.eldorado.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Eldorado_process))
        if self.bethoven.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Bethoven_process))
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
