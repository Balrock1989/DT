from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName('Dialog')
        Dialog.resize(500, 200)

        self.sephora = QtWidgets.QCheckBox(Dialog)
        self.sephora.setGeometry(QtCore.QRect(10, 10, 20, 20))
        self.sephora.setObjectName('sephora')
        self.label_sephora = QtWidgets.QLabel(Dialog)
        self.label_sephora.setGeometry(QtCore.QRect(30, 5, 90, 30))
        self.label_sephora.setObjectName('label_sephora')

        # self.ildebote = QtWidgets.QCheckBox(Dialog)
        # self.ildebote.setGeometry(QtCore.QRect(10, 30, 20, 20))
        # self.ildebote.setObjectName('ildebote')
        # self.label_ildebote = QtWidgets.QLabel(Dialog)
        # self.label_ildebote.setGeometry(QtCore.QRect(30, 25, 90, 30))
        # self.label_ildebote.setObjectName('label_ildebote')

        self.thomas = QtWidgets.QCheckBox(Dialog)
        self.thomas.setGeometry(QtCore.QRect(10, 30, 20, 20))
        self.thomas.setObjectName('thomas')
        self.label_thomas = QtWidgets.QLabel(Dialog)
        self.label_thomas.setGeometry(QtCore.QRect(30, 25, 90, 30))
        self.label_thomas.setObjectName('label_thomas')

        # self.kupivip = QtWidgets.QCheckBox(Dialog)
        # self.kupivip.setGeometry(QtCore.QRect(10, 50, 20, 20))
        # self.kupivip.setObjectName('kupivip')
        # self.label_kupivip = QtWidgets.QLabel(Dialog)
        # self.label_kupivip.setGeometry(QtCore.QRect(30, 45, 90, 30))
        # self.label_kupivip.setObjectName('label_kupivip')

        self.braun = QtWidgets.QCheckBox(Dialog)
        self.braun.setGeometry(QtCore.QRect(10, 50, 20, 20))
        self.braun.setObjectName('braun')
        self.label_braun = QtWidgets.QLabel(Dialog)
        self.label_braun.setGeometry(QtCore.QRect(30, 45, 90, 30))
        self.label_braun.setObjectName('label_braun')

        # self.akusherstvo = QtWidgets.QCheckBox(Dialog)
        # self.akusherstvo.setGeometry(QtCore.QRect(10, 70, 20, 20))
        # self.akusherstvo.setObjectName('akusherstvo')
        # self.label_akusherstvo = QtWidgets.QLabel(Dialog)
        # self.label_akusherstvo.setGeometry(QtCore.QRect(30, 65, 90, 30))
        # self.label_akusherstvo.setObjectName('label_akusherstvo')

        self.mixit = QtWidgets.QCheckBox(Dialog)
        self.mixit.setGeometry(QtCore.QRect(10, 70, 20, 20))
        self.mixit.setObjectName('mixit')
        self.label_mixit = QtWidgets.QLabel(Dialog)
        self.label_mixit.setGeometry(QtCore.QRect(30, 65, 90, 30))
        self.label_mixit.setObjectName('label_mixit')

        self.utkonos = QtWidgets.QCheckBox(Dialog)
        self.utkonos.setGeometry(QtCore.QRect(10, 90, 20, 20))
        self.utkonos.setObjectName('utkonos')
        self.label_utkonos = QtWidgets.QLabel(Dialog)
        self.label_utkonos.setGeometry(QtCore.QRect(30, 85, 90, 30))
        self.label_utkonos.setObjectName('label_utkonos')

        self.vseinstrumenti = QtWidgets.QCheckBox(Dialog)
        self.vseinstrumenti.setGeometry(QtCore.QRect(10, 110, 20, 20))
        self.vseinstrumenti.setObjectName('vseinstrumenti')
        self.label_vseinstrumenti = QtWidgets.QLabel(Dialog)
        self.label_vseinstrumenti.setGeometry(QtCore.QRect(30, 105, 90, 30))
        self.label_vseinstrumenti.setObjectName('label_vseinstrumenti')

        # self.butic = QtWidgets.QCheckBox(Dialog)
        # self.butic.setGeometry(QtCore.QRect(10, 130, 20, 20))
        # self.butic.setObjectName('butic')
        # self.label_butic = QtWidgets.QLabel(Dialog)
        # self.label_butic.setGeometry(QtCore.QRect(30, 125, 90, 30))
        # self.label_butic.setObjectName('label_butic')

        self.miele_shop = QtWidgets.QCheckBox(Dialog)
        self.miele_shop.setGeometry(QtCore.QRect(10, 130, 20, 20))
        self.miele_shop.setObjectName('miele_shop')
        self.label_miele_shop = QtWidgets.QLabel(Dialog)
        self.label_miele_shop.setGeometry(QtCore.QRect(30, 125, 90, 30))
        self.label_miele_shop.setObjectName('label_miele_shop')

        self.book = QtWidgets.QCheckBox(Dialog)
        self.book.setGeometry(QtCore.QRect(130, 10, 20, 20))
        self.book.setObjectName('book')
        self.label_book = QtWidgets.QLabel(Dialog)
        self.label_book.setGeometry(QtCore.QRect(150, 5, 90, 30))
        self.label_book.setObjectName('label_book')

        self.holodilnik = QtWidgets.QCheckBox(Dialog)
        self.holodilnik.setGeometry(QtCore.QRect(130, 30, 20, 20))
        self.holodilnik.setObjectName('holodilnik')
        self.label_holodilnik = QtWidgets.QLabel(Dialog)
        self.label_holodilnik.setGeometry(QtCore.QRect(150, 25, 90, 30))
        self.label_holodilnik.setObjectName('label_holodilnik')

        self.kolesadarom = QtWidgets.QCheckBox(Dialog)
        self.kolesadarom.setGeometry(QtCore.QRect(130, 50, 20, 20))
        self.kolesadarom.setObjectName('kolesadarom')
        self.label_kolesadarom = QtWidgets.QLabel(Dialog)
        self.label_kolesadarom.setGeometry(QtCore.QRect(150, 45, 90, 30))
        self.label_kolesadarom.setObjectName('label_kolesadarom')

        # self.volt = QtWidgets.QCheckBox(Dialog)
        # self.volt.setGeometry(QtCore.QRect(130, 70, 20, 20))
        # self.volt.setObjectName('volt')
        # self.label_volt = QtWidgets.QLabel(Dialog)
        # self.label_volt.setGeometry(QtCore.QRect(150, 65, 90, 30))
        # self.label_volt.setObjectName('label_volt')

        # self.respublica = QtWidgets.QCheckBox(Dialog)
        # self.respublica.setGeometry(QtCore.QRect(130, 90, 20, 20))
        # self.respublica.setObjectName('respublica')
        # self.label_respublica = QtWidgets.QLabel(Dialog)
        # self.label_respublica.setGeometry(QtCore.QRect(150, 85, 90, 30))
        # self.label_respublica.setObjectName('label_respublica')

        self.svyaznoy = QtWidgets.QCheckBox(Dialog)
        self.svyaznoy.setGeometry(QtCore.QRect(130, 110, 20, 20))
        self.svyaznoy.setObjectName('svyaznoy')
        self.label_svyaznoy = QtWidgets.QLabel(Dialog)
        self.label_svyaznoy.setGeometry(QtCore.QRect(150, 105, 90, 30))
        self.label_svyaznoy.setObjectName('label_svyaznoy')

        self.pharmacosmetica = QtWidgets.QCheckBox(Dialog)
        self.pharmacosmetica.setGeometry(QtCore.QRect(130, 130, 20, 20))
        self.pharmacosmetica.setObjectName('svyaznoy')
        self.label_pharmacosmetica = QtWidgets.QLabel(Dialog)
        self.label_pharmacosmetica.setGeometry(QtCore.QRect(150, 125, 90, 30))
        self.label_pharmacosmetica.setObjectName('label_pharmacosmetica')

        self.mts = QtWidgets.QCheckBox(Dialog)
        self.mts.setGeometry(QtCore.QRect(250, 10, 20, 20))
        self.mts.setObjectName('mts')
        self.label_mts = QtWidgets.QLabel(Dialog)
        self.label_mts.setGeometry(QtCore.QRect(270, 5, 90, 30))
        self.label_mts.setObjectName('label_mts')

        self.rivegauche = QtWidgets.QCheckBox(Dialog)
        self.rivegauche.setGeometry(QtCore.QRect(250, 30, 20, 20))
        self.rivegauche.setObjectName('rivegauche')
        self.label_rivegauche = QtWidgets.QLabel(Dialog)
        self.label_rivegauche.setGeometry(QtCore.QRect(270, 25, 90, 30))
        self.label_rivegauche.setObjectName('label_rivegauche')

        self.la_roche = QtWidgets.QCheckBox(Dialog)
        self.la_roche.setGeometry(QtCore.QRect(250, 50, 20, 20))
        self.la_roche.setObjectName('la_roche')
        self.label_la_roche = QtWidgets.QLabel(Dialog)
        self.label_la_roche.setGeometry(QtCore.QRect(270, 45, 90, 30))
        self.label_la_roche.setObjectName('label_la_roche')

        self.rozetka = QtWidgets.QCheckBox(Dialog)
        self.rozetka.setGeometry(QtCore.QRect(250, 70, 20, 20))
        self.rozetka.setObjectName('rozetka')
        self.label_rozetka = QtWidgets.QLabel(Dialog)
        self.label_rozetka.setGeometry(QtCore.QRect(270, 65, 90, 30))
        self.label_rozetka.setObjectName('label_rozetka')

        # self.eldorado = QtWidgets.QCheckBox(Dialog)
        # self.eldorado.setGeometry(QtCore.QRect(250, 90, 20, 20))
        # self.eldorado.setObjectName('eldorado')
        # self.label_eldorado = QtWidgets.QLabel(Dialog)
        # self.label_eldorado.setGeometry(QtCore.QRect(270, 85, 90, 30))
        # self.label_eldorado.setObjectName('label_eldorado')

        self.bethoven = QtWidgets.QCheckBox(Dialog)
        self.bethoven.setGeometry(QtCore.QRect(250, 110, 20, 20))
        self.bethoven.setObjectName('bethoven')
        self.label_bethoven = QtWidgets.QLabel(Dialog)
        self.label_bethoven.setGeometry(QtCore.QRect(270, 105, 90, 30))
        self.label_bethoven.setObjectName('label_bethoven')

        self.toy = QtWidgets.QCheckBox(Dialog)
        self.toy.setGeometry(QtCore.QRect(250, 130, 20, 20))
        self.toy.setObjectName('toy')
        self.label_toy = QtWidgets.QLabel(Dialog)
        self.label_toy.setGeometry(QtCore.QRect(270, 125, 90, 30))
        self.label_toy.setObjectName('label_toy')

        self.labirint = QtWidgets.QCheckBox(Dialog)
        self.labirint.setGeometry(QtCore.QRect(370, 10, 20, 20))
        self.labirint.setObjectName('labirint')
        self.label_labirint = QtWidgets.QLabel(Dialog)
        self.label_labirint.setGeometry(QtCore.QRect(390, 5, 90, 30))
        self.label_labirint.setObjectName('label_labirint')

        self.santehnika_tut = QtWidgets.QCheckBox(Dialog)
        self.santehnika_tut.setGeometry(QtCore.QRect(370, 30, 20, 20))
        self.santehnika_tut.setObjectName('santehnika_tut')
        self.label_santehnika_tut = QtWidgets.QLabel(Dialog)
        self.label_santehnika_tut.setGeometry(QtCore.QRect(390, 25, 90, 30))
        self.label_santehnika_tut.setObjectName('label_santehnika_tut')

        self.maxi_pro = QtWidgets.QCheckBox(Dialog)
        self.maxi_pro.setGeometry(QtCore.QRect(370, 50, 20, 20))
        self.maxi_pro.setObjectName('maxi_pro')
        self.label_maxi_pro = QtWidgets.QLabel(Dialog)
        self.label_maxi_pro.setGeometry(QtCore.QRect(390, 45, 90, 30))
        self.label_maxi_pro.setObjectName('label_maxi_pro')

        self.interes_1c = QtWidgets.QCheckBox(Dialog)
        self.interes_1c.setGeometry(QtCore.QRect(370, 70, 20, 20))
        self.interes_1c.setObjectName('interes_1c')
        self.label_interes_1c = QtWidgets.QLabel(Dialog)
        self.label_interes_1c.setGeometry(QtCore.QRect(390, 65, 90, 30))
        self.label_interes_1c.setObjectName('label_interes_1c')

        self.philips = QtWidgets.QCheckBox(Dialog)
        self.philips.setGeometry(QtCore.QRect(370, 90, 20, 20))
        self.philips.setObjectName('philips')
        self.label_philips = QtWidgets.QLabel(Dialog)
        self.label_philips.setGeometry(QtCore.QRect(390, 85, 90, 30))
        self.label_philips.setObjectName('label_philips')

        self.domovoy = QtWidgets.QCheckBox(Dialog)
        self.domovoy.setGeometry(QtCore.QRect(370, 110, 20, 20))
        self.domovoy.setObjectName('domovoy')
        self.label_domovoy = QtWidgets.QLabel(Dialog)
        self.label_domovoy.setGeometry(QtCore.QRect(390, 105, 90, 30))
        self.label_domovoy.setObjectName('label_domovoy')

        self.kotofoto = QtWidgets.QCheckBox(Dialog)
        self.kotofoto.setGeometry(QtCore.QRect(370, 130, 20, 20))
        self.kotofoto.setObjectName('kotofoto')
        self.label_kotofoto = QtWidgets.QLabel(Dialog)
        self.label_kotofoto.setGeometry(QtCore.QRect(390, 125, 90, 30))
        self.label_kotofoto.setObjectName('label_kotofoto')

        self.ok = QtWidgets.QPushButton(Dialog)
        self.ok.setGeometry(QtCore.QRect(300, 160, 90, 30))
        self.ok.setObjectName('ok')
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ok.setFont(font)

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font = QtGui.QFont()
        font.setPointSize(10)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate('Dialog', 'Dialog'))
        self.ok.setText(_translate('Dialog', 'ENTER'))
        self.label_sephora.setText(_translate('Dialog', 'Sephora'))
        # self.label_ildebote.setText(_translate('Dialog', 'Иль Дэ Ботэ'))
        self.label_thomas.setText(_translate('Dialog', 'Thomas-Munz'))
        self.label_braun.setText(_translate('Dialog', 'Braun'))
        self.label_mixit.setText(_translate('Dialog', 'Mixit'))
        self.label_utkonos.setText(_translate('Dialog', 'Утконос'))
        self.label_vseinstrumenti.setText(_translate('Dialog', 'Все инструменты'))
        self.label_miele_shop.setText(_translate('Dialog', 'Miele_shop'))
        self.label_book.setText(_translate('Dialog', 'Book24'))
        self.label_holodilnik.setText(_translate('Dialog', 'Холодильник'))
        self.label_kolesadarom.setText(_translate('Dialog', 'Колеса даром'))
        # self.label_volt.setText(_translate('Dialog', '220 Volt'))
        # self.label_respublica.setText(_translate('Dialog', 'Республика'))
        self.label_svyaznoy.setText(_translate('Dialog', 'Связной'))
        self.label_pharmacosmetica.setText(_translate('Dialog', 'ФармКосметика'))
        self.label_mts.setText(_translate('Dialog', 'МТС'))
        self.label_rivegauche.setText(_translate('Dialog', 'Ривгош'))
        self.label_la_roche.setText(_translate('Dialog', 'La Roche Posay'))
        self.label_rozetka.setText(_translate('Dialog', 'Розетка'))
        # self.label_eldorado.setText(_translate('Dialog', 'Эльдорадо'))
        self.label_bethoven.setText(_translate('Dialog', 'Бетховен'))
        self.label_toy.setText(_translate('Dialog', 'Toy'))
        self.label_labirint.setText(_translate('Dialog', 'Лабиринт'))
        self.label_santehnika_tut.setText(_translate('Dialog', 'СантехникаТут'))
        self.label_maxi_pro.setText(_translate('Dialog', 'МаксиПро'))
        self.label_interes_1c.setText(_translate('Dialog', '1С_Интерес'))
        self.label_philips.setText(_translate('Dialog', 'Philips'))
        self.label_domovoy.setText(_translate('Dialog', 'Домовой'))
        self.label_kotofoto.setText(_translate('Dialog', 'Котофото'))

