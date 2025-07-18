"""
===============================================================================
fileName: machineMonitor.machineManager.main
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import sys
from functools import partial

# ==== third ==== #
from PySide2 import QtWidgets

# ==== local ===== #
from machineMonitor.library.general.uiLib import applyStyleSheet
from machineMonitor.library.general.uiLib import loadUi

# ==== global ==== #


class MachineManager:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.storeWidget()
        self.fillUi()
        self.connectWidgets()
        applyStyleSheet(self.ui)
        self.initializeUi()

    def storeWidget(self):
        self.nameField = self.ui.nameField
        self.infoLayout = self.ui.infoLayout
        self.endButton = self.ui.endButton
        self.infoLine = self.ui.infoLine
        self.uiMenus = self.ui.uiMenus

    def fillUi(self):
        print('fillUi')

    def connectWidgets(self):
        print('connectWidgets')

    def initializeUi(self, *args):
        if QtWidgets.QApplication.instance() is None:
            self.app = QtWidgets.QApplication(sys.argv)
        else:
            self.app = QtWidgets.QApplication.instance()

        if isinstance(self.ui, QtWidgets.QDialog):
            self.ui.exec_()
        else:
            self.ui.show()


if __name__ == "__main__":
    MachineManager()