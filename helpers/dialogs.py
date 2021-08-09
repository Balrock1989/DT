from PyQt5.QtWidgets import QDialog

from design.custom_dialog_parser import Ui_Dialog as Ui_Dialog_parser
from design.custom_dialog_resizer import Ui_Dialog as Ui_Dialog_resizer
from helpers.StartNewProcess import StartNewProcess
from parsers.process_braun import BraunProcess
from parsers.process_miele_shop import MieleProcess
from parsers.process_mixit import MixitProcess
from parsers.process_philips import PhilipsProcess
from parsers.process_1c_interes import Interes_1c_process
from parsers.process_bethoven import BethovenProcess
from parsers.process_book import BookProcess
from parsers.process_holodilnik import HolodilnikProcess
from parsers.process_kolesadarom import KolesadaromProcess
from parsers.process_kotofoto import KotofotoProcess
from parsers.process_la_roche import LaRocheProcess
from parsers.process_labirint import LabirintProcess
from parsers.process_maxi_pro import MaxiProProcess
from parsers.process_mts import MtsProcess
from parsers.process_pharmacosmetica import PharmacosmeticaProcess
from parsers.process_rivegauche import RivegaucheProcess
from parsers.process_rozetka import RozetkaProcess
from parsers.process_santehnika_tut import SantehnikaTutProcess
from parsers.process_sephora import SephoraProcess
from parsers.process_svyaznoy import SvyaznoyProcess
from parsers.process_tddomovoy import DomovoyProcess
from parsers.process_thomas import ThomasProcess
from parsers.process_toy import ToyProcess
from parsers.process_utkonos import UtkonosProcess
from parsers.process_vseintrumenti import VseinstrumentiProcess


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
            processes.append(StartNewProcess(self.mainwindow, SephoraProcess))
        if self.thomas.isChecked():
            processes.append(StartNewProcess(self.mainwindow, ThomasProcess))
        if self.braun.isChecked():
            processes.append(StartNewProcess(self.mainwindow, BraunProcess))
        if self.mixit.isChecked():
            processes.append(StartNewProcess(self.mainwindow, MixitProcess))
        if self.utkonos.isChecked():
            processes.append(StartNewProcess(self.mainwindow, UtkonosProcess))
        if self.vseinstrumenti.isChecked():
            processes.append(StartNewProcess(self.mainwindow, VseinstrumentiProcess))
        if self.miele_shop.isChecked():
            processes.append(StartNewProcess(self.mainwindow, MieleProcess))
        if self.book.isChecked():
            processes.append(StartNewProcess(self.mainwindow, BookProcess))
        if self.holodilnik.isChecked():
            processes.append(StartNewProcess(self.mainwindow, HolodilnikProcess))
        if self.kolesadarom.isChecked():
            processes.append(StartNewProcess(self.mainwindow, KolesadaromProcess))
        # if self.volt.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Volt_process))
        # if self.respublica.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Respublica_process))
        if self.svyaznoy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, SvyaznoyProcess))
        if self.pharmacosmetica.isChecked():
            processes.append(StartNewProcess(self.mainwindow, PharmacosmeticaProcess))
        if self.mts.isChecked():
            processes.append(StartNewProcess(self.mainwindow, MtsProcess))
        if self.rivegauche.isChecked():
            processes.append(StartNewProcess(self.mainwindow, RivegaucheProcess))
        if self.la_roche.isChecked():
            processes.append(StartNewProcess(self.mainwindow, LaRocheProcess))
        if self.rozetka.isChecked():
            processes.append(StartNewProcess(self.mainwindow, RozetkaProcess))
        # if self.eldorado.isChecked():
        #     processes.append(StartNewProcess(self.mainwindow, Eldorado_process))
        if self.bethoven.isChecked():
            processes.append(StartNewProcess(self.mainwindow, BethovenProcess))
        if self.toy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, ToyProcess))
        if self.labirint.isChecked():
            processes.append(StartNewProcess(self.mainwindow, LabirintProcess))
        if self.santehnika_tut.isChecked():
            processes.append(StartNewProcess(self.mainwindow, SantehnikaTutProcess))
        if self.maxi_pro.isChecked():
            processes.append(StartNewProcess(self.mainwindow, MaxiProProcess))
        if self.interes_1c.isChecked():
            processes.append(StartNewProcess(self.mainwindow, Interes_1c_process))
        if self.philips.isChecked():
            processes.append(StartNewProcess(self.mainwindow, PhilipsProcess))
        if self.domovoy.isChecked():
            processes.append(StartNewProcess(self.mainwindow, DomovoyProcess))
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
