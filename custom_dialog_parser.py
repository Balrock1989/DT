from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName('Dialog')
        Dialog.resize(280, 200)

        self.sephora = QtWidgets.QCheckBox(Dialog)
        self.sephora.setGeometry(QtCore.QRect(10, 10, 20, 20))
        self.sephora.setObjectName('sephora')
        self.label_sephora = QtWidgets.QLabel(Dialog)
        self.label_sephora.setGeometry(QtCore.QRect(30, 5, 250, 30))
        self.label_sephora.setObjectName('label_sephora')

        self.ildebote = QtWidgets.QCheckBox(Dialog)
        self.ildebote.setGeometry(QtCore.QRect(10, 30, 20, 20))
        self.ildebote.setObjectName('ildebote')
        self.label_ildebote = QtWidgets.QLabel(Dialog)
        self.label_ildebote.setGeometry(QtCore.QRect(30, 25, 250, 30))
        self.label_ildebote.setObjectName('label_ildebote')

        self.kupivip = QtWidgets.QCheckBox(Dialog)
        self.kupivip.setGeometry(QtCore.QRect(10, 50, 20, 20))
        self.kupivip.setObjectName('kupivip')
        self.label_kupivip = QtWidgets.QLabel(Dialog)
        self.label_kupivip.setGeometry(QtCore.QRect(30, 45, 250, 30))
        self.label_kupivip.setObjectName('label_kupivip')

        self.akusherstvo = QtWidgets.QCheckBox(Dialog)
        self.akusherstvo.setGeometry(QtCore.QRect(10, 70, 20, 20))
        self.akusherstvo.setObjectName('akusherstvo')
        self.label_akusherstvo = QtWidgets.QLabel(Dialog)
        self.label_akusherstvo.setGeometry(QtCore.QRect(30, 65, 250, 30))
        self.label_akusherstvo.setObjectName('label_akusherstvo')

        self.utkonos = QtWidgets.QCheckBox(Dialog)
        self.utkonos.setGeometry(QtCore.QRect(10, 90, 20, 20))
        self.utkonos.setObjectName('utkonos')
        self.label_utkonos = QtWidgets.QLabel(Dialog)
        self.label_utkonos.setGeometry(QtCore.QRect(30, 85, 250, 30))
        self.label_utkonos.setObjectName('label_utkonos')

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

