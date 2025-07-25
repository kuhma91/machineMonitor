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
import json
from datetime import datetime
from functools import partial

# ==== third ==== #
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon

# ==== local ===== #
from machineMonitor.library.general.uiLib import applyStyleSheet
from machineMonitor.library.general.uiLib import confirmDialog
from machineMonitor.library.general.uiLib import loadUi
from machineMonitor.library.general.uiLib import STYLE_SHEET
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.logger.core import LOG_TYPES, getTempData
from machineMonitor.logger.core import ICON_FOLDER
from machineMonitor.logger.core import NO_MACHINE_CMD
from machineMonitor.logger.core import saveData
from machineMonitor.logger.core import clearTempData

# ==== global ==== #


class Logger:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.uiMenus = self.ui.uiMenus

        self.unfolded = False
        self.fromTemp = None
        self.mode = 'create'

        clearTempData()

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

        tempData = getTempData()
        if not tempData:
            return

        else:
            choice = confirmDialog(message='temp file found ! do you want to load it ?')
            if not choice:
                return

            latestDateStr = max(tempData.keys(), key=lambda ds: datetime.strptime(ds, '%Y_%m_%d'))
            lastestFile = tempData[latestDateStr]
            with open(lastestFile, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.machineBox.setCurrentText(data.get('machineName', ''))
            self.logBox.setCurrentText(data.get('type'))
            self.projectField.setText(data.get('project', ''))
            self.commentField.setPlainText(data.get('comment', ''))

            self.fromTemp = tempData[latestDateStr]

            self.endButton.setEnabled(True)

    def connectWidgets(self):
        self.machineBox.currentTextChanged.connect(partial(self.changeMachineCommand))
        self.projectField.textChanged.connect(partial(self.checkValidity))
        self.commentButton.clicked.connect(partial(self.foldCommand))
        self.endButton.clicked.connect(partial(self.saveCommand))

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
        machine = self.machineBox.currentText()
        data = {
            'machineName': machine,
            'type': self.logBox.currentText(),
            'project': self.projectField.text(),
            'comment': self.commentField.toPlainText()
        }
        saveData(data, temp=not machine)

        if self.fromTemp:
            os.remove(self.fromTemp)

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