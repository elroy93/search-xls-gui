# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLayout, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QTextBrowser, QVBoxLayout, QWidget)

class Ui_search_widget(object):
    def setupUi(self, search_widget):
        if not search_widget.objectName():
            search_widget.setObjectName(u"search_widget")
        search_widget.resize(886, 720)
        self.verticalLayout = QVBoxLayout(search_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.input_grid = QGridLayout()
        self.input_grid.setObjectName(u"input_grid")
        self.input_grid.setSizeConstraint(QLayout.SetFixedSize)
        self.le_input_search_text = QLineEdit(search_widget)
        self.le_input_search_text.setObjectName(u"le_input_search_text")

        self.input_grid.addWidget(self.le_input_search_text, 2, 1, 1, 1)

        self.label = QLabel(search_widget)
        self.label.setObjectName(u"label")

        self.input_grid.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cb_is_strict = QCheckBox(search_widget)
        self.cb_is_strict.setObjectName(u"cb_is_strict")

        self.horizontalLayout.addWidget(self.cb_is_strict)

        self.cb_is_match_case = QCheckBox(search_widget)
        self.cb_is_match_case.setObjectName(u"cb_is_match_case")

        self.horizontalLayout.addWidget(self.cb_is_match_case)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.input_grid.addLayout(self.horizontalLayout, 3, 0, 1, 2)

        self.btn_search = QPushButton(search_widget)
        self.btn_search.setObjectName(u"btn_search")

        self.input_grid.addWidget(self.btn_search, 2, 2, 1, 1)

        self.label_3 = QLabel(search_widget)
        self.label_3.setObjectName(u"label_3")

        self.input_grid.addWidget(self.label_3, 2, 0, 1, 1)

        self.le_input_dir = QLineEdit(search_widget)
        self.le_input_dir.setObjectName(u"le_input_dir")

        self.input_grid.addWidget(self.le_input_dir, 0, 1, 1, 1)

        self.btn_open_dir = QPushButton(search_widget)
        self.btn_open_dir.setObjectName(u"btn_open_dir")

        self.input_grid.addWidget(self.btn_open_dir, 0, 2, 1, 1)

        self.le_input_file_filter = QLineEdit(search_widget)
        self.le_input_file_filter.setObjectName(u"le_input_file_filter")

        self.input_grid.addWidget(self.le_input_file_filter, 1, 1, 1, 1)

        self.label_2 = QLabel(search_widget)
        self.label_2.setObjectName(u"label_2")

        self.input_grid.addWidget(self.label_2, 1, 0, 1, 1)


        self.verticalLayout.addLayout(self.input_grid)

        self.table_search_result = QTableWidget(search_widget)
        self.table_search_result.setObjectName(u"table_search_result")

        self.verticalLayout.addWidget(self.table_search_result)

        self.tb_console = QTextBrowser(search_widget)
        self.tb_console.setObjectName(u"tb_console")
        self.tb_console.setMaximumSize(QSize(16777215, 120))

        self.verticalLayout.addWidget(self.tb_console)


        self.retranslateUi(search_widget)

        QMetaObject.connectSlotsByName(search_widget)
    # setupUi

    def retranslateUi(self, search_widget):
        search_widget.setWindowTitle(QCoreApplication.translate("search_widget", u"Form", None))
        self.le_input_search_text.setText(QCoreApplication.translate("search_widget", u"content", None))
        self.label.setText(QCoreApplication.translate("search_widget", u"\u6253\u5f00\u76ee\u5f55 : ", None))
        self.cb_is_strict.setText(QCoreApplication.translate("search_widget", u"\u4e25\u683c\u6a21\u5f0f", None))
        self.cb_is_match_case.setText(QCoreApplication.translate("search_widget", u"\u5927\u5c0f\u5199\u5339\u914d", None))
        self.btn_search.setText(QCoreApplication.translate("search_widget", u"\u641c\u7d22", None))
        self.label_3.setText(QCoreApplication.translate("search_widget", u"\u67e5\u627e\u5185\u5bb9 :", None))
        self.le_input_dir.setText(QCoreApplication.translate("search_widget", u"D:/xls", None))
        self.btn_open_dir.setText(QCoreApplication.translate("search_widget", u"\u6253\u5f00", None))
        self.le_input_file_filter.setPlaceholderText(QCoreApplication.translate("search_widget", u"input the file name ,you want , `!mail` represent doest search files which filename contain `mail`", None))
        self.label_2.setText(QCoreApplication.translate("search_widget", u"\u6587\u4ef6\u8fc7\u6ee4 : ", None))
    # retranslateUi

