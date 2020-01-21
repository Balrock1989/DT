# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design3.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName('DTMainWindow')
        MainWindow.resize(869, 489)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')
        self.path_window = QtWidgets.QTextBrowser(self.centralwidget)
        self.path_window.setGeometry(QtCore.QRect(10, 30, 681, 31))
        self.path_window.setObjectName('path_window')
        self.path_buttom = QtWidgets.QPushButton(self.centralwidget)
        self.path_buttom.setGeometry(QtCore.QRect(700, 30, 140, 31))

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.path_buttom.setFont(font)
        self.path_buttom.setObjectName('path_buttom')
        self.path_buttom.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(True)
        font.setWeight(50)

        self.partner_name = QtWidgets.QTextEdit(self.centralwidget)
        self.partner_name.setGeometry(QtCore.QRect(580, 160, 261, 25))
        self.partner_name.setObjectName('date_start')

        self.partner_name_label = QtWidgets.QLabel(self.centralwidget)
        self.partner_name_label.setGeometry(QtCore.QRect(610, 140, 201, 16))
        self.partner_name_label.setFont(font)
        self.partner_name_label.setTextFormat(QtCore.Qt.AutoText)
        self.partner_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.partner_name_label.setObjectName('data_start_label')

        self.date_start = QtWidgets.QTextEdit(self.centralwidget)
        self.date_start.setGeometry(QtCore.QRect(580, 220, 261, 25))
        self.date_start.setObjectName('date_start')

        self.data_start_label = QtWidgets.QLabel(self.centralwidget)
        self.data_start_label.setGeometry(QtCore.QRect(610, 200, 201, 16))
        self.data_start_label.setFont(font)
        self.data_start_label.setTextFormat(QtCore.Qt.AutoText)
        self.data_start_label.setAlignment(QtCore.Qt.AlignCenter)
        self.data_start_label.setObjectName('data_start_label')

        self.date_end = QtWidgets.QTextEdit(self.centralwidget)
        self.date_end.setGeometry(QtCore.QRect(580, 280, 261, 25))
        self.date_end.setObjectName('date_end')

        self.data_end_label = QtWidgets.QLabel(self.centralwidget)
        self.data_end_label.setGeometry(QtCore.QRect(600, 260, 211, 16))
        self.data_end_label.setFont(font)
        self.data_end_label.setAlignment(QtCore.Qt.AlignCenter)
        self.data_end_label.setObjectName('data_end_label')

        self.url = QtWidgets.QTextEdit(self.centralwidget)
        self.url.setGeometry(QtCore.QRect(580, 340, 261, 25))
        self.url.setObjectName('url')

        self.url_label = QtWidgets.QLabel(self.centralwidget)
        self.url_label.setGeometry(QtCore.QRect(620, 320, 191, 16))
        self.url_label.setFont(font)
        self.url_label.setAlignment(QtCore.Qt.AlignCenter)
        self.url_label.setObjectName('url_label')

        self.rename_button = QtWidgets.QPushButton(self.centralwidget)
        self.rename_button.setGeometry(QtCore.QRect(580, 400, 131, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.rename_button.setFont(font)
        self.rename_button.setObjectName('rename_button')
        self.rename_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.rename_checbox = QtWidgets.QCheckBox(self.centralwidget)
        self.rename_checbox.setGeometry(QtCore.QRect(580, 375, 161, 20))
        self.rename_checbox.setObjectName('rename_checbox')

        self.run_browser = QtWidgets.QPushButton(self.centralwidget)
        self.run_browser.setGeometry(QtCore.QRect(580, 80, 131, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.run_browser.setFont(font)
        self.run_browser.setObjectName('browser')
        self.run_browser.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.parser_button = QtWidgets.QPushButton(self.centralwidget)
        self.parser_button.setGeometry(QtCore.QRect(720, 80, 131, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.parser_button.setFont(font)
        self.parser_button.setObjectName('парсер')
        self.parser_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.command_window = QtWidgets.QTextBrowser(self.centralwidget)
        self.command_window.setGeometry(QtCore.QRect(10, 80, 551, 381))
        self.command_window.setObjectName('command_window')

        self.path_label = QtWidgets.QLabel(self.centralwidget)
        self.path_label.setGeometry(QtCore.QRect(10, 10, 191, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(True)
        font.setWeight(50)
        self.path_label.setFont(font)
        self.path_label.setObjectName('path_label')

        self.resize_buttom = QtWidgets.QPushButton(self.centralwidget)
        self.resize_buttom.setGeometry(QtCore.QRect(720, 400, 131, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.resize_buttom.setFont(font)
        self.resize_buttom.setObjectName('resize_buttom')
        self.resize_buttom.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName('statusbar')
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('DTMainWindow', 'DTMainWindow'))
        self.path_window.setPlaceholderText(
            _translate('MainWindow', 'Путь до папки с баннерами которые будут переименованы'))
        self.path_buttom.setText(_translate('MainWindow', 'Выбрать папку ...'))
        self.partner_name_label.setText(_translate('MainWindow', 'ИМЯ ПАРТНЕРА:'))
        self.partner_name.setPlaceholderText(_translate('MainWindow', 'Для загрузки данных из таблицы'))
        self.data_start_label.setText(_translate('MainWindow', 'ДАТА НАЧАЛА АКЦИИ:'))
        self.date_start.setPlaceholderText(_translate('MainWindow', 'Пример 01.01.2019, если пусто то текущая дата'))
        self.date_end.setPlaceholderText(_translate('MainWindow', 'Пример 31.12.2019, если есть'))
        self.data_end_label.setText(_translate('MainWindow', 'ДАТА ОКОНЧАНИЯ АКЦИИ:'))
        self.url_label.setText(_translate('MainWindow', 'ССЫЛКА НА АКЦИЮ:'))
        self.url.setPlaceholderText(_translate('MainWindow', 'URL акции если есть'))
        self.rename_button.setText(_translate('MainWindow', 'Переименовать'))
        self.rename_checbox.setText(_translate('MainWindow', 'В одну папку'))
        self.run_browser.setText(_translate('MainWindow', 'Браузер'))
        self.parser_button.setText(_translate('MainWindow', 'Парсер'))
        self.command_window.setPlaceholderText(_translate('MainWindow', ''))
        self.path_label.setText(_translate('MainWindow', 'Путь до папки с баннерами:'))
        self.resize_buttom.setText(_translate('MainWindow', 'Изменить размер'))
