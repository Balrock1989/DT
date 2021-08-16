from PyQt5.QtWidgets import QDialog

from design.UiDialogParser import UiDialogParser as Ui_Dialog_parser
from design.UiDialogResizer import UiDialogResizer as Ui_Dialog_resizer
from helpers.StartNewProcess import StartNewProcess
from parsers.MagnitAptekaProcess import MagnitAptekaProcess
from parsers.BraunProcess import BraunProcess
from parsers.MieleProcess import MieleProcess
from parsers.MixitProcess import MixitProcess
from parsers.PhilipsProcess import PhilipsProcess
from parsers.InteresProcess import InteresProcess
from parsers.BethovenProcess import BethovenProcess
from parsers.BookProcess import BookProcess
from parsers.HolodilnikProcess import HolodilnikProcess
from parsers.KolesadaromProcess import KolesadaromProcess
from parsers.KotofotoProcess import KotofotoProcess
from parsers.LaRocheProcess import LaRocheProcess
from parsers.LabirintProcess import LabirintProcess
from parsers.MaxiProProcess import MaxiProProcess
from parsers.MtsProcess import MtsProcess
from parsers.PharmacosmeticaProcess import PharmacosmeticaProcess
from parsers.RivegaucheProcess import RivegaucheProcess
from parsers.RozetkaProcess import RozetkaProcess
from parsers.SantehnikaTutProcess import SantehnikaTutProcess
from parsers.SephoraProcess import SephoraProcess
from parsers.SvyaznoyProcess import SvyaznoyProcess
from parsers.DomovoyProcess import DomovoyProcess
from parsers.ThomasProcess import ThomasProcess
from parsers.ToyProcess import ToyProcess
from parsers.UtkonosProcess import UtkonosProcess
from parsers.VseinstrumentiProcess import VseinstrumentiProcess


class CustomDialogParser(QDialog, Ui_Dialog_parser):
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
        if self.magnit_apteka.isChecked():
            processes.append(StartNewProcess(self.mainwindow, MagnitAptekaProcess))
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
            processes.append(StartNewProcess(self.mainwindow, InteresProcess))
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


class CustomDialogResizer(QDialog, Ui_Dialog_resizer):
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
