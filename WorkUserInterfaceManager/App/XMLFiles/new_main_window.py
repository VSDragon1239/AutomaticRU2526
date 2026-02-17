# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMdiArea, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1012, 600)
        MainWindow.setMinimumSize(QSize(1000, 600))
        MainWindow.setStyleSheet(u"QWidget {\n"
"	border: 1px solid rgb(0, 100, 100);\n"
"	color: rgb(100, 200, 200);\n"
"	background-color: rgba(20, 30, 40, 100);\n"
"	border-radius: 3px;\n"
"	padding: 3px;\n"
"}\n"
"\n"
"/* ==================  \u041a\u043d\u043e\u043f\u043a\u0438  ================== */\n"
"\n"
"QPushButton {  \n"
"    background-color: rgb(10, 80, 100);\n"
"    color: rgb(100, 200, 200);\n"
"	border-radius: 5px;\n"
"	padding: 3px 5px;\n"
"	margin: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120);\n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80);\n"
"}\n"
"\n"
"/* ==================  \u0413\u043b\u0430\u0432\u043d\u0430\u044f / \u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u044f  ================== */\n"
"\n"
"QTabWidget::pane {\n"
"    border: 1px solid rgb(0, 100, 100);\n"
"    background-color: rgba(0, 30, 40, 180);\n"
"}\n"
"\n"
"QTabBar {\n"
"    background: rgba(0, 10, 80, 100);\n"
"    border-bottom: 1px solid rgb(0, 100, 100)"
                        ";\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    color: rgb(100, 200, 200);\n"
"    padding: 6px 12px;\n"
"    border: 1px solid rgb(0, 100, 100);\n"
"    border-bottom: none;\n"
"    min-width: 80px;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    color: rgb(180, 255, 255);\n"
"	background: rgb(0, 60, 80);\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    background: rgb(0, 60, 80);\n"
"}\n"
"\n"
"QTabBar::tab:!selected {\n"
"    margin-top: 3px;\n"
"}\n"
"")
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.action_2 = QAction(MainWindow)
        self.action_2.setObjectName(u"action_2")
        self.action_3 = QAction(MainWindow)
        self.action_3.setObjectName(u"action_3")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(500, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.QW1111_3 = QWidget(self.widget)
        self.QW1111_3.setObjectName(u"QW1111_3")
        self.QW1111_3.setStyleSheet(u"")
        self.verticalLayout_11 = QVBoxLayout(self.QW1111_3)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.LL11111_GPLabel = QLabel(self.QW1111_3)
        self.LL11111_GPLabel.setObjectName(u"LL11111_GPLabel")
        self.LL11111_GPLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_11.addWidget(self.LL11111_GPLabel)

        self.listWidget = QListWidget(self.QW1111_3)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setStyleSheet(u"")

        self.verticalLayout_11.addWidget(self.listWidget)

        self.BTN11112 = QPushButton(self.QW1111_3)
        self.BTN11112.setObjectName(u"BTN11112")

        self.verticalLayout_11.addWidget(self.BTN11112)


        self.verticalLayout_2.addWidget(self.QW1111_3)

        self.QW1111412 = QWidget(self.widget)
        self.QW1111412.setObjectName(u"QW1111412")
        self.QW1111412.setStyleSheet(u"")
        self.verticalLayout_25 = QVBoxLayout(self.QW1111412)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.QL11114121_2 = QLabel(self.QW1111412)
        self.QL11114121_2.setObjectName(u"QL11114121_2")
        self.QL11114121_2.setStyleSheet(u"")
        self.QL11114121_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_25.addWidget(self.QL11114121_2)

        self.comboBox_4 = QComboBox(self.QW1111412)
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setEditable(False)

        self.verticalLayout_25.addWidget(self.comboBox_4)

        self.lineEdit_5 = QLineEdit(self.QW1111412)
        self.lineEdit_5.setObjectName(u"lineEdit_5")

        self.verticalLayout_25.addWidget(self.lineEdit_5)

        self.listWidget_4 = QListWidget(self.QW1111412)
        self.listWidget_4.setObjectName(u"listWidget_4")
        self.listWidget_4.setStyleSheet(u"")

        self.verticalLayout_25.addWidget(self.listWidget_4)

        self.BTN11114122_2 = QPushButton(self.QW1111412)
        self.BTN11114122_2.setObjectName(u"BTN11114122_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN11114122_2.sizePolicy().hasHeightForWidth())
        self.BTN11114122_2.setSizePolicy(sizePolicy)

        self.verticalLayout_25.addWidget(self.BTN11114122_2)


        self.verticalLayout_2.addWidget(self.QW1111412)


        self.horizontalLayout.addWidget(self.widget)

        self.ProjectManagerTabs = QTabWidget(self.centralwidget)
        self.ProjectManagerTabs.setObjectName(u"ProjectManagerTabs")
        self.ProjectManagerTabs.setStyleSheet(u"")
        self.Main = QWidget()
        self.Main.setObjectName(u"Main")
        self.verticalLayout_3 = QVBoxLayout(self.Main)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.QW1111411_2 = QWidget(self.Main)
        self.QW1111411_2.setObjectName(u"QW1111411_2")
        self.QW1111411_2.setStyleSheet(u"")
        self.verticalLayout_24 = QVBoxLayout(self.QW1111411_2)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.QL11114112_2 = QLabel(self.QW1111411_2)
        self.QL11114112_2.setObjectName(u"QL11114112_2")
        self.QL11114112_2.setStyleSheet(u"")
        self.QL11114112_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_24.addWidget(self.QL11114112_2)

        self.mdiArea = QMdiArea(self.QW1111411_2)
        self.mdiArea.setObjectName(u"mdiArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mdiArea.sizePolicy().hasHeightForWidth())
        self.mdiArea.setSizePolicy(sizePolicy1)

        self.verticalLayout_24.addWidget(self.mdiArea)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.BTN11114123_3 = QPushButton(self.QW1111411_2)
        self.BTN11114123_3.setObjectName(u"BTN11114123_3")
        sizePolicy.setHeightForWidth(self.BTN11114123_3.sizePolicy().hasHeightForWidth())
        self.BTN11114123_3.setSizePolicy(sizePolicy)
        self.BTN11114123_3.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")

        self.horizontalLayout_4.addWidget(self.BTN11114123_3)

        self.BTN11114116_3 = QPushButton(self.QW1111411_2)
        self.BTN11114116_3.setObjectName(u"BTN11114116_3")
        sizePolicy.setHeightForWidth(self.BTN11114116_3.sizePolicy().hasHeightForWidth())
        self.BTN11114116_3.setSizePolicy(sizePolicy)
        self.BTN11114116_3.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0px;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")
        self.BTN11114116_3.setIconSize(QSize(32, 32))

        self.horizontalLayout_4.addWidget(self.BTN11114116_3)

        self.BTN11114116_4 = QPushButton(self.QW1111411_2)
        self.BTN11114116_4.setObjectName(u"BTN11114116_4")
        sizePolicy.setHeightForWidth(self.BTN11114116_4.sizePolicy().hasHeightForWidth())
        self.BTN11114116_4.setSizePolicy(sizePolicy)
        self.BTN11114116_4.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")
        self.BTN11114116_4.setIconSize(QSize(32, 32))

        self.horizontalLayout_4.addWidget(self.BTN11114116_4)


        self.verticalLayout_24.addLayout(self.horizontalLayout_4)


        self.verticalLayout_3.addWidget(self.QW1111411_2)

        self.ProjectManagerTabs.addTab(self.Main, "")
        self.Projects = QWidget()
        self.Projects.setObjectName(u"Projects")
        self.horizontalLayout_8 = QHBoxLayout(self.Projects)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.QW1111411 = QWidget(self.Projects)
        self.QW1111411.setObjectName(u"QW1111411")
        self.QW1111411.setStyleSheet(u"")
        self.verticalLayout_23 = QVBoxLayout(self.QW1111411)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.QL11114112 = QLabel(self.QW1111411)
        self.QL11114112.setObjectName(u"QL11114112")
        self.QL11114112.setStyleSheet(u"")
        self.QL11114112.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.QL11114112)

        self.listWidget_7 = QListWidget(self.QW1111411)
        self.listWidget_7.setObjectName(u"listWidget_7")
        self.listWidget_7.setStyleSheet(u"")

        self.verticalLayout_23.addWidget(self.listWidget_7)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.BTN11114123_2 = QPushButton(self.QW1111411)
        self.BTN11114123_2.setObjectName(u"BTN11114123_2")
        sizePolicy.setHeightForWidth(self.BTN11114123_2.sizePolicy().hasHeightForWidth())
        self.BTN11114123_2.setSizePolicy(sizePolicy)
        self.BTN11114123_2.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")

        self.horizontalLayout_3.addWidget(self.BTN11114123_2)

        self.BTN11114116_2 = QPushButton(self.QW1111411)
        self.BTN11114116_2.setObjectName(u"BTN11114116_2")
        sizePolicy.setHeightForWidth(self.BTN11114116_2.sizePolicy().hasHeightForWidth())
        self.BTN11114116_2.setSizePolicy(sizePolicy)
        self.BTN11114116_2.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0px;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")
        self.BTN11114116_2.setIconSize(QSize(32, 32))

        self.horizontalLayout_3.addWidget(self.BTN11114116_2)

        self.BTN11114116 = QPushButton(self.QW1111411)
        self.BTN11114116.setObjectName(u"BTN11114116")
        sizePolicy.setHeightForWidth(self.BTN11114116.sizePolicy().hasHeightForWidth())
        self.BTN11114116.setSizePolicy(sizePolicy)
        self.BTN11114116.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")
        self.BTN11114116.setIconSize(QSize(32, 32))

        self.horizontalLayout_3.addWidget(self.BTN11114116)


        self.verticalLayout_23.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_8.addWidget(self.QW1111411)

        self.ProjectManagerTabs.addTab(self.Projects, "")
        self.Docs = QWidget()
        self.Docs.setObjectName(u"Docs")
        self.verticalLayout_4 = QVBoxLayout(self.Docs)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.QW1111411_3 = QWidget(self.Docs)
        self.QW1111411_3.setObjectName(u"QW1111411_3")
        self.QW1111411_3.setStyleSheet(u"")
        self.verticalLayout_26 = QVBoxLayout(self.QW1111411_3)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.QL11114112_3 = QLabel(self.QW1111411_3)
        self.QL11114112_3.setObjectName(u"QL11114112_3")
        self.QL11114112_3.setStyleSheet(u"")
        self.QL11114112_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_26.addWidget(self.QL11114112_3)

        self.mdiArea_2 = QMdiArea(self.QW1111411_3)
        self.mdiArea_2.setObjectName(u"mdiArea_2")
        sizePolicy1.setHeightForWidth(self.mdiArea_2.sizePolicy().hasHeightForWidth())
        self.mdiArea_2.setSizePolicy(sizePolicy1)

        self.verticalLayout_26.addWidget(self.mdiArea_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.BTN11114123_4 = QPushButton(self.QW1111411_3)
        self.BTN11114123_4.setObjectName(u"BTN11114123_4")
        sizePolicy.setHeightForWidth(self.BTN11114123_4.sizePolicy().hasHeightForWidth())
        self.BTN11114123_4.setSizePolicy(sizePolicy)
        self.BTN11114123_4.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")

        self.horizontalLayout_5.addWidget(self.BTN11114123_4)

        self.BTN11114116_5 = QPushButton(self.QW1111411_3)
        self.BTN11114116_5.setObjectName(u"BTN11114116_5")
        sizePolicy.setHeightForWidth(self.BTN11114116_5.sizePolicy().hasHeightForWidth())
        self.BTN11114116_5.setSizePolicy(sizePolicy)
        self.BTN11114116_5.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0px;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")
        self.BTN11114116_5.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.BTN11114116_5)

        self.BTN11114116_6 = QPushButton(self.QW1111411_3)
        self.BTN11114116_6.setObjectName(u"BTN11114116_6")
        sizePolicy.setHeightForWidth(self.BTN11114116_6.sizePolicy().hasHeightForWidth())
        self.BTN11114116_6.setSizePolicy(sizePolicy)
        self.BTN11114116_6.setStyleSheet(u"QPushButton {  \n"
"    background-color: rgb(10, 80, 100); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 */  \n"
"    color: rgb(100, 200, 200); /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 */\n"
"	border-radius: 0;\n"
"}  \n"
"  \n"
"QPushButton:hover {  \n"
"    background-color: rgb(20, 100, 120); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */  \n"
"}  \n"
"  \n"
"QPushButton:pressed {  \n"
"    background-color: rgb(0, 60, 80); /* \u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u043f\u0440\u0438 \u043d\u0430\u0436\u0430\u0442\u0438\u0438 */  \n"
"}")
        self.BTN11114116_6.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.BTN11114116_6)


        self.verticalLayout_26.addLayout(self.horizontalLayout_5)


        self.verticalLayout_4.addWidget(self.QW1111411_3)

        self.ProjectManagerTabs.addTab(self.Docs, "")

        self.horizontalLayout.addWidget(self.ProjectManagerTabs)

        self.ApplicationsManagerTabs = QTabWidget(self.centralwidget)
        self.ApplicationsManagerTabs.setObjectName(u"ApplicationsManagerTabs")
        self.ApplicationsManagerTabs.setMaximumSize(QSize(300, 16777215))
        self.ApplicationsManagerTabs.setStyleSheet(u"")
        self.Projects_2 = QWidget()
        self.Projects_2.setObjectName(u"Projects_2")
        self.horizontalLayout_10 = QHBoxLayout(self.Projects_2)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.QW1111_4 = QWidget(self.Projects_2)
        self.QW1111_4.setObjectName(u"QW1111_4")
        self.QW1111_4.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.QW1111_4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.QL11114121_3 = QLabel(self.QW1111_4)
        self.QL11114121_3.setObjectName(u"QL11114121_3")
        self.QL11114121_3.setStyleSheet(u"")
        self.QL11114121_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.QL11114121_3)

        self.lineEdit_7 = QLineEdit(self.QW1111_4)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit_7.sizePolicy().hasHeightForWidth())
        self.lineEdit_7.setSizePolicy(sizePolicy2)

        self.verticalLayout.addWidget(self.lineEdit_7)

        self.listWidget_5 = QListWidget(self.QW1111_4)
        self.listWidget_5.setObjectName(u"listWidget_5")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.listWidget_5.sizePolicy().hasHeightForWidth())
        self.listWidget_5.setSizePolicy(sizePolicy3)
        self.listWidget_5.setViewMode(QListView.ViewMode.IconMode)

        self.verticalLayout.addWidget(self.listWidget_5)

        self.BTN11111_2 = QPushButton(self.QW1111_4)
        self.BTN11111_2.setObjectName(u"BTN11111_2")

        self.verticalLayout.addWidget(self.BTN11111_2)


        self.horizontalLayout_10.addWidget(self.QW1111_4)

        self.ApplicationsManagerTabs.addTab(self.Projects_2, "")
        self.Docs_2 = QWidget()
        self.Docs_2.setObjectName(u"Docs_2")
        self.horizontalLayout_11 = QHBoxLayout(self.Docs_2)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.QW1111_2 = QWidget(self.Docs_2)
        self.QW1111_2.setObjectName(u"QW1111_2")
        self.QW1111_2.setStyleSheet(u"")
        self._2 = QVBoxLayout(self.QW1111_2)
        self._2.setObjectName(u"_2")
        self.LL11111_Addons = QLabel(self.QW1111_2)
        self.LL11111_Addons.setObjectName(u"LL11111_Addons")
        sizePolicy2.setHeightForWidth(self.LL11111_Addons.sizePolicy().hasHeightForWidth())
        self.LL11111_Addons.setSizePolicy(sizePolicy2)
        self.LL11111_Addons.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self._2.addWidget(self.LL11111_Addons, 0, Qt.AlignmentFlag.AlignVCenter)

        self.lineEdit = QLineEdit(self.QW1111_2)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy2.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy2)

        self._2.addWidget(self.lineEdit)

        self.listWidget_2 = QListWidget(self.QW1111_2)
        self.listWidget_2.setObjectName(u"listWidget_2")
        sizePolicy3.setHeightForWidth(self.listWidget_2.sizePolicy().hasHeightForWidth())
        self.listWidget_2.setSizePolicy(sizePolicy3)
        self.listWidget_2.setStyleSheet(u"")
        self.listWidget_2.setViewMode(QListView.ViewMode.IconMode)

        self._2.addWidget(self.listWidget_2)

        self.BTN11111 = QPushButton(self.QW1111_2)
        self.BTN11111.setObjectName(u"BTN11111")

        self._2.addWidget(self.BTN11111)


        self.horizontalLayout_11.addWidget(self.QW1111_2)

        self.ApplicationsManagerTabs.addTab(self.Docs_2, "")

        self.horizontalLayout.addWidget(self.ApplicationsManagerTabs)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1012, 41))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)
        self.menu.addAction(self.action_3)

        self.retranslateUi(MainWindow)

        self.ProjectManagerTabs.setCurrentIndex(0)
        self.ApplicationsManagerTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u0435", None))
        self.action_2.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0435\u0440\u0432\u0435\u0440", None))
        self.action_3.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0438\u0437\u0430\u0446\u0438\u044f", None))
        self.LL11111_GPLabel.setText(QCoreApplication.translate("MainWindow", u"\u0413\u043b\u043e\u0431\u0430\u043b\u044c\u043d\u044b\u0435 \u041f\u0440\u043e\u0435\u043a\u0442\u044b", None))
        self.BTN11112.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043d\u043e\u0432\u044b\u0439 \u0413\u041f", None))
        self.QL11114121_2.setText(QCoreApplication.translate("MainWindow", u"         \u0421\u043f\u0438\u0441\u043e\u043a \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432         ", None))
        self.comboBox_4.setItemText(0, QCoreApplication.translate("MainWindow", u"\u0411\u0435\u0437 \u0444\u0438\u043b\u044c\u0442\u0440\u0430 \u0442\u0438\u043f\u0430", None))
        self.comboBox_4.setItemText(1, QCoreApplication.translate("MainWindow", u"Python", None))
        self.comboBox_4.setItemText(2, QCoreApplication.translate("MainWindow", u"Blender", None))
        self.comboBox_4.setItemText(3, QCoreApplication.translate("MainWindow", u"UnrealEngine", None))
        self.comboBox_4.setItemText(4, QCoreApplication.translate("MainWindow", u"Painting", None))
        self.comboBox_4.setItemText(5, QCoreApplication.translate("MainWindow", u"Imagers", None))

        self.comboBox_4.setCurrentText(QCoreApplication.translate("MainWindow", u"\u0411\u0435\u0437 \u0444\u0438\u043b\u044c\u0442\u0440\u0430 \u0442\u0438\u043f\u0430", None))
        self.lineEdit_5.setText("")
        self.lineEdit_5.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a", None))
        self.BTN11114122_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043d\u043e\u0432\u044b\u0439 \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.QL11114112_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c!", None))
        self.BTN11114123_3.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
#if QT_CONFIG(tooltip)
        self.BTN11114116_3.setToolTip(QCoreApplication.translate("MainWindow", u"\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0442\u0438\u043f\u044b: \u0417\u0430\u043c\u0435\u0442\u043a\u0438; \u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f; \u0414\u0440\u0443\u0433\u0438\u0435", None))
#endif // QT_CONFIG(tooltip)
        self.BTN11114116_3.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f", None))
#if QT_CONFIG(tooltip)
        self.BTN11114116_4.setToolTip(QCoreApplication.translate("MainWindow", u"\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0442\u0438\u043f\u044b: \u0417\u0430\u043c\u0435\u0442\u043a\u0438; \u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f; \u0414\u0440\u0443\u0433\u0438\u0435", None))
#endif // QT_CONFIG(tooltip)
        self.BTN11114116_4.setText(QCoreApplication.translate("MainWindow", u"\u0427\u0442\u043e \u0442\u043e \u043d\u043e\u0432\u043e\u0435...", None))
        self.ProjectManagerTabs.setTabText(self.ProjectManagerTabs.indexOf(self.Main), QCoreApplication.translate("MainWindow", u"\u0413\u043b\u0430\u0432\u043d\u0430\u044f", None))
        self.QL11114112.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u0435\u043a\u0442\u0430...", None))
        self.BTN11114123_2.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
#if QT_CONFIG(tooltip)
        self.BTN11114116_2.setToolTip(QCoreApplication.translate("MainWindow", u"\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0442\u0438\u043f\u044b: \u0417\u0430\u043c\u0435\u0442\u043a\u0438; \u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f; \u0414\u0440\u0443\u0433\u0438\u0435", None))
#endif // QT_CONFIG(tooltip)
        self.BTN11114116_2.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0434\u0435\u043b\u0430\u0442\u044c \u0440\u0435\u0437\u0435\u0440\u0432\u043d\u0443\u044e \u043a\u043e\u043f\u0438\u044e", None))
#if QT_CONFIG(tooltip)
        self.BTN11114116.setToolTip(QCoreApplication.translate("MainWindow", u"\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0442\u0438\u043f\u044b: \u0417\u0430\u043c\u0435\u0442\u043a\u0438; \u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f; \u0414\u0440\u0443\u0433\u0438\u0435", None))
#endif // QT_CONFIG(tooltip)
        self.BTN11114116.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442...", None))
        self.ProjectManagerTabs.setTabText(self.ProjectManagerTabs.indexOf(self.Projects), QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0435\u043a\u0442\u044b", None))
        self.QL11114112_3.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u0438 \u043f\u0440\u043e\u0435\u043a\u0442\u0430 {\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435}", None))
        self.BTN11114123_4.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
#if QT_CONFIG(tooltip)
        self.BTN11114116_5.setToolTip(QCoreApplication.translate("MainWindow", u"\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0442\u0438\u043f\u044b: \u0417\u0430\u043c\u0435\u0442\u043a\u0438; \u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f; \u0414\u0440\u0443\u0433\u0438\u0435", None))
#endif // QT_CONFIG(tooltip)
        self.BTN11114116_5.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f", None))
#if QT_CONFIG(tooltip)
        self.BTN11114116_6.setToolTip(QCoreApplication.translate("MainWindow", u"\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u0442\u0438\u043f\u044b: \u0417\u0430\u043c\u0435\u0442\u043a\u0438; \u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f; \u0414\u0440\u0443\u0433\u0438\u0435", None))
#endif // QT_CONFIG(tooltip)
        self.BTN11114116_6.setText(QCoreApplication.translate("MainWindow", u"\u0427\u0442\u043e \u0442\u043e \u043d\u043e\u0432\u043e\u0435...", None))
        self.ProjectManagerTabs.setTabText(self.ProjectManagerTabs.indexOf(self.Docs), QCoreApplication.translate("MainWindow", u"\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b", None))
        self.QL11114121_3.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f", None))
        self.lineEdit_7.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a", None))
        self.BTN11111_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442", None))
        self.ApplicationsManagerTabs.setTabText(self.ApplicationsManagerTabs.indexOf(self.Projects_2), QCoreApplication.translate("MainWindow", u"\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f", None))
        self.LL11111_Addons.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0435 \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u044b", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a", None))
        self.BTN11111.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440\u0438\u044e", None))
        self.ApplicationsManagerTabs.setTabText(self.ApplicationsManagerTabs.indexOf(self.Docs_2), QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
    # retranslateUi

