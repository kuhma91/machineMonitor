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
from machineMonitor.library.general.uiLib import STYLE_SHEET
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.logger.core import LOG_TYPES
from machineMonitor.logger.core import ICON_FOLDER
from machineMonitor.logger.core import NO_MACHINE_CMD
from machineMonitor.logger.core import saveData

# ==== global ==== #


class Logger:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.uiMenus = self.ui.uiMenus

        self.unfolded = False
        self.mode = 'create'

        self.storeWidget()
        self.fillUi()
        self.connectWidgets()
        applyStyleSheet(self.ui, excluded=self.uiMenus['excluded'])
        self.initializeUi()

    def storeWidget(self):
        self.machineBox = self.ui.machineBox
        self.infoLine = self.ui.infoLine
        self.logBox = self.ui.logBox
        self.projectField = self.ui.projectField
        self.commentButton = self.ui.commentButton
        self.commentField = self.ui.commentField
        self.endButton = self.ui.endButton
        self.cancelButton = self.ui.cancelButton

    def fillUi(self):
        machines = ['']
        machines.extend(sorted(list(getMachineData())))
        self.machineBox.addItems(machines)
        self.logBox.addItems(LOG_TYPES)

        # tempData = getTempData()


    def connectWidgets(self):
        self.machineBox.currentTextChanged.connect(partial(self.changeMachineCommand))
        self.projectField.textChanged.connect(partial(self.checkValidity))
        self.commentButton.clicked.connect(partial(self.foldCommand))
        self.endButton.clicked.connect(partial(self.saveCommand))
        for name, button in self.uiMenus.get('optionButtons', {}).items():
            button.clicked.connect(partial(self.optionCommand, name))

    def checkValidity(self, *args):
        project = self.projectField.text()
        self.endButton.setEnabled(len(project) > 3)

    def changeMachineCommand(self, *args):
        if not self.machineBox.currentText():
            text = '    temporary'
            cmd = NO_MACHINE_CMD
            visibility = True
        else:
            text = '    save'
            cmd = STYLE_SHEET['QComboBox']
            visibility = False

        self.infoLine.setVisible(visibility)
        self.machineBox.setStyleSheet(cmd)
        self.endButton.setText(text)
        self.ui.adjustSize()


    def foldCommand(self, *args):
        icon = 'folded.png' if self.unfolded else 'unfolded.png'
        self.commentButton.setIcon(QIcon(os.path.join(ICON_FOLDER, icon)))
        self.unfolded = not self.unfolded
        self.commentField.setVisible(self.unfolded)
        self.ui.adjustSize()

    def saveCommand(self, *args):
        if self.mode == 'create':
            machine = self.machineBox.currentText()
            data = {
                'machineName': machine,
                'type': self.logBox.currentText(),
                'project': self.projectField.text(),
                'comment': self.commentField.toPlainText()
            }
            saveData(data, temp=not machine)


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