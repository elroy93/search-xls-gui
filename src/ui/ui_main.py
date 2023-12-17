# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTableWidget, QTableWidgetItem,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1158, 682)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.input_grid = QGridLayout()
        self.input_grid.setObjectName(u"input_grid")
        self.input_grid.setSizeConstraint(QLayout.SetFixedSize)
        self.le_input_search_text = QLineEdit(self.centralwidget)
        self.le_input_search_text.setObjectName(u"le_input_search_text")

        self.input_grid.addWidget(self.le_input_search_text, 2, 1, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.input_grid.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.input_grid.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.input_grid.addWidget(self.label, 0, 0, 1, 1)

        self.le_input_file_filter = QLineEdit(self.centralwidget)
        self.le_input_file_filter.setObjectName(u"le_input_file_filter")

        self.input_grid.addWidget(self.le_input_file_filter, 1, 1, 1, 1)

        self.btn_open_dir = QPushButton(self.centralwidget)
        self.btn_open_dir.setObjectName(u"btn_open_dir")

        self.input_grid.addWidget(self.btn_open_dir, 0, 2, 1, 1)

        self.le_input_dir = QLineEdit(self.centralwidget)
        self.le_input_dir.setObjectName(u"le_input_dir")

        self.input_grid.addWidget(self.le_input_dir, 0, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox_2 = QCheckBox(self.centralwidget)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.horizontalLayout.addWidget(self.checkBox_2)

        self.checkBox = QCheckBox(self.centralwidget)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout.addWidget(self.checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.input_grid.addLayout(self.horizontalLayout, 3, 0, 1, 2)

        self.btn_search = QPushButton(self.centralwidget)
        self.btn_search.setObjectName(u"btn_search")

        self.input_grid.addWidget(self.btn_search, 2, 2, 1, 1)


        self.verticalLayout.addLayout(self.input_grid)

        self.grid_table = QGridLayout()
        self.grid_table.setObjectName(u"grid_table")
        self.grid_table.setSizeConstraint(QLayout.SetMaximumSize)
        self.table_search_result = QTableWidget(self.centralwidget)
        self.table_search_result.setObjectName(u"table_search_result")

        self.grid_table.addWidget(self.table_search_result, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.grid_table)

        self.grid_console = QGridLayout()
        self.grid_console.setObjectName(u"grid_console")
        self.grid_console.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.tb_console = QTextBrowser(self.centralwidget)
        self.tb_console.setObjectName(u"tb_console")
        self.tb_console.setMinimumSize(QSize(0, 150))
        self.tb_console.setMaximumSize(QSize(16777215, 200))

        self.grid_console.addWidget(self.tb_console, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.grid_console)

        self.verticalLayout.setStretch(1, 10)
        self.verticalLayout.setStretch(2, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1158, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.le_input_search_text.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6\u8fc7\u6ee4 : ", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u67e5\u627e\u5185\u5bb9 :", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u76ee\u5f55 : ", None))
        self.btn_open_dir.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00", None))
        self.le_input_dir.setText(QCoreApplication.translate("MainWindow", u"D:/code/searchXlsGui/src/mock", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"\u4e25\u683c\u6a21\u5f0f", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"\u5927\u5c0f\u5199\u5339\u914d", None))
        self.btn_search.setText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22", None))
    # retranslateUi

