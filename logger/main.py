"""
===============================================================================
fileName: machineMonitor.logger.main
scripter: angiu
creation date: 22/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import sys
from functools import partial

# ==== third ==== #
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon

# ==== local ===== #
from machineMonitor.library.general.uiLib import applyStyleSheet
from machineMonitor.library.general.uiLib import loadUi
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.logger.core import LOG_TYPES
from machineMonitor.logger.core import ICON_FOLDER

# ==== global ==== #


class Logger:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.uiMenus = self.ui.uiMenus

        self.unfolded = False

        self.storeWidget()
        self.fillUi()
        self.connectWidgets()
        applyStyleSheet(self.ui, excluded=self.uiMenus['excluded'])
        self.initializeUi()

    def storeWidget(self):
        self.machineBox = self.ui.machineBox
        self.logBox = self.ui.logBox
        self.projectField = self.ui.projectField
        self.commentButton = self.ui.commentButton
        self.commentField = self.ui.commentField
        self.endButton = self.ui.endButton
        self.cancelButton = self.ui.cancelButton

    def fillUi(self):
        self.machineBox.addItems(sorted(list(getMachineData())))
        self.logBox.addItems(LOG_TYPES)

    def connectWidgets(self):
        self.projectField.textChanged.connect(partial(self.checkValidity))
        self.commentButton.clicked.connect(partial(self.foldCommand))
        for name, button in self.uiMenus.get('optionButtons', {}).items():
            button.clicked.connect(partial(self.optionCommand, name))

    def checkValidity(self, *args):
        project = self.projectField.text()
        self.endButton.setEnabled(len(project) > 3)

    def foldCommand(self, *args):
        icon = 'folded.png' if self.unfolded else 'unfolded.png'
        self.commentButton.setIcon(QIcon(os.path.join(ICON_FOLDER, icon)))
        self.unfolded = not self.unfolded
        self.commentField.setVisible(self.unfolded)
        self.ui.adjustSize()

    def optionCommand(self, name, *args):
        print(name)

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
    Logger()