from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName('Dialog')
        Dialog.resize(280, 200)

        self.sephora = QtWidgets.QCheckBox(Dialog)
        self.sephora.setGeometry(QtCore.QRect(10, 10, 20, 20))
        self.sephora.setObjectName('sephora')
        self.label_sephora = QtWidgets.QLabel(Dialog)
        self.label_sephora.setGeometry(QtCore.QRect(30, 5, 90, 30))
        self.label_sephora.setObjectName('label_sephora')

        self.ildebote = QtWidgets.QCheckBox(Dialog)
        self.ildebote.setGeometry(QtCore.QRect(10, 30, 20, 20))
        self.ildebote.setObjectName('ildebote')
        self.label_ildebote = QtWidgets.QLabel(Dialog)
        self.label_ildebote.setGeometry(QtCore.QRect(30, 25, 90, 30))
        self.label_ildebote.setObjectName('label_ildebote')

        self.kupivip = QtWidgets.QCheckBox(Dialog)
        self.kupivip.setGeometry(QtCore.QRect(10, 50, 20, 20))
        self.kupivip.setObjectName('kupivip')
        self.label_kupivip = QtWidgets.QLabel(Dialog)
        self.label_kupivip.setGeometry(QtCore.QRect(30, 45, 90, 30))
        self.label_kupivip.setObjectName('label_kupivip')

        self.akusherstvo = QtWidgets.QCheckBox(Dialog)
        self.akusherstvo.setGeometry(QtCore.QRect(10, 70, 20, 20))
        self.akusherstvo.setObjectName('akusherstvo')
        self.label_akusherstvo = QtWidgets.QLabel(Dialog)
        self.label_akusherstvo.setGeometry(QtCore.QRect(30, 65, 90, 30))
        self.label_akusherstvo.setObjectName('label_akusherstvo')

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

        self.butic = QtWidgets.QCheckBox(Dialog)
        self.butic.setGeometry(QtCore.QRect(10, 130, 20, 20))
        self.butic.setObjectName('butic')
        self.label_butic = QtWidgets.QLabel(Dialog)
        self.label_butic.setGeometry(QtCore.QRect(30, 125, 90, 30))
        self.label_butic.setObjectName('label_butic')

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


        self.ok = QtWidgets.QPushButton(Dialog)
        self.ok.setGeometry(QtCore.QRect(170, 150, 90, 30))
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
        self.label_ildebote.setText(_translate('Dialog', 'Иль Дэ Ботэ'))
        self.label_kupivip.setText(_translate('Dialog', 'КупиВип'))
        self.label_akusherstvo.setText(_translate('Dialog', 'Акушерство'))
        self.label_utkonos.setText(_translate('Dialog', 'Утконос'))
        self.label_vseinstrumenti.setText(_translate('Dialog', 'Все инструменты'))
        self.label_butic.setText(_translate('Dialog', 'Бутик'))
        self.label_book.setText(_translate('Dialog', 'Book24'))
        self.label_holodilnik.setText(_translate('Dialog', 'Холодильник'))


