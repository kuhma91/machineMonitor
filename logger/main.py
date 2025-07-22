"""
===============================================================================
fileName: machineMonitor.logger.main
scripter: angiu
creation date: 22/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import sys
from functools import partial

# ==== third ==== #
from PySide2 import QtWidgets

# ==== local ===== #
from library.general.uiLib import getMayaMainWindow
from library.general.uiLib import applyStyleSheet
from library.general.uiLib import loadUi

# ==== global ==== #
MAYA_ENV = getMayaMainWindow()


class MachineMonitorLogger:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.storeWidget()
        self.fillUi()
        self.connectWidgets()
        applyStyleSheet(self.ui)
        self.initializeUi()

    def storeWidget(self):
        print('storeWidget')

    def fillUi(self):
        print('fillUi')

    def connectWidgets(self):
        print('connectWidgets')

    def initializeUi(self, *args):
        if MAYA_ENV:
            from library.maya.windowLib import dockPySide2UI, closeWindow
            closeWindow(self.ui)
            dockPySide2UI(self.ui)
        else:
            if QtWidgets.QApplication.instance() is None:
                self.app = QtWidgets.QApplication(sys.argv)
            else:
                self.app = QtWidgets.QApplication.instance()

            if isinstance(self.ui, QtWidgets.QDialog):
                self.ui.exec_()
            else:
                self.ui.show()


if __name__ == "__main__":
    if not MAYA_ENV:
        MachineMonitorLogger()