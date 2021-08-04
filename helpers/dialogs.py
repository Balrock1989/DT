from PyQt5.QtWidgets import QDialog

from design.custom_dialog_parser import Ui_Dialog as Ui_Dialog_parser
from design.custom_dialog_resizer import Ui_Dialog as Ui_Dialog_resizer
from helpers.start_new_process import StartNewProcess
from parsers.philips import Philips_process
from parsers.process_1c_interes import Interes_1c_process
from parsers.process_bethoven import Bethoven_process
from parsers.process_book import Book_process
from parsers.process_holodilnik import Holodilnik_process
from parsers.process_kolesadarom import Kolesadarom_process
from parsers.process_kotofoto import KotofotoProcess
from parsers.process_la_roche import La_roche_process
from parsers.process_labirint import Labirint_process
from parsers.process_maxi_pro import Maxi_pro_process
from parsers.process_mts import MtsProcess
from parsers.process_pharmacosmetica import Pharmacosmetica_process
from parsers.process_rivegauche import Rivegauche_process
from parsers.process_rozetka import Rozetka_process
from parsers.process_santehnika_tut import Santehnika_tut_process
from parsers.process_sephora import Sephora_process
from parsers.process_svyaznoy import Svyaznoy_process
from parsers.process_tddomovoy import Domovoy_process
from parsers.process_thomas import Thomas_process
from parsers.process_toy import Toy_process
from parsers.process_utkonos import Utkonos_process
from parsers.process_vseintrumenti import Vseinstrumenti_process


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
        if self.thomas.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Thomas_process))
        # if self.kupivip.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Kupivip_process))
        # if self.akusherstvo.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Akusherstvo_process))
        if self.utkonos.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Utkonos_process))
        if self.vseinstrumenti.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Vseinstrumenti_process))
        # if self.butic.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Butic_process))
        if self.book.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Book_process))
        if self.holodilnik.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Holodilnik_process))
        if self.kolesadarom.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Kolesadarom_process))
        # if self.volt.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Volt_process))
        # if self.respublica.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Respublica_process))
        if self.svyaznoy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Svyaznoy_process))
        if self.pharmacosmetica.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Pharmacosmetica_process))
        if self.mts.isChecked():
            processes.append(StartNewProcess(self.mainwindow, MtsProcess))
        if self.rivegauche.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Rivegauche_process))
        if self.la_roche.isChecked():
            processes.append(StartNewProcess(self.mainwindow, La_roche_process))
        if self.rozetka.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Rozetka_process))
        # if self.eldorado.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Eldorado_process))
        if self.bethoven.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Bethoven_process))
        if self.toy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Toy_process))
        if self.labirint.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Labirint_process))
        if self.santehnika_tut.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Santehnika_tut_process))
        if self.maxi_pro.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Maxi_pro_process))
        if self.interes_1c.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Interes_1c_process))
        if self.philips.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Philips_process))
        if self.domovoy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Domovoy_process))
        if self.kotofoto.isChecked():
            processes.append(StartNewProcess(self.mainwindow, KotofotoProcess))
        [process.start() for process in processes]
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
