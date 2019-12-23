# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(280, 200)

        self.textEdit = QtWidgets.QLineEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(20, 110, 240, 30))
        self.textEdit.setObjectName("textEdit")

        self.ok = QtWidgets.QPushButton(Dialog)
        self.ok.setGeometry(QtCore.QRect(170, 150, 90, 30))
        self.ok.setObjectName("ok")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ok.setFont(font)

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 80, 250, 30))
        self.label.setObjectName("label")

        self.label2 = QtWidgets.QLabel(Dialog)
        self.label2.setGeometry(QtCore.QRect(0, 35, 280, 30))
        self.label2.setObjectName("label2")
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label2.setFont(font)
        self.label2.setAlignment(QtCore.Qt.AlignCenter)

        self.label3 = QtWidgets.QLabel(Dialog)
        self.label3.setGeometry(QtCore.QRect(0, 5, 280, 30))
        self.label3.setObjectName("label3")
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label3.setFont(font)
        self.label3.setAlignment(QtCore.Qt.AlignCenter)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.ok.setText(_translate("Dialog", "ENTER"))
        self.label.setText(_translate("Dialog", "Введите размер:"))
        self.label2.setText(_translate("Dialog", "Размеры"))
        self.label3.setText(_translate("Dialog", "Текущий размер:"))
