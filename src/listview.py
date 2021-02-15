# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'listview.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(348, 604)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setToolTip("")
        Dialog.setWhatsThis("")
        self.listMacros = QtWidgets.QListWidget(Dialog)
        self.listMacros.setGeometry(QtCore.QRect(10, 10, 321, 571))
        self.listMacros.setMaximumSize(QtCore.QSize(2000, 2000))
        self.listMacros.setSizeIncrement(QtCore.QSize(200, 200))
        self.listMacros.setToolTip("")
        self.listMacros.setWhatsThis("")
        self.listMacros.setObjectName("listMacros")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Macro list"))
