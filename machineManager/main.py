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
from machineMonitor.library.general.infoLib import COLORS
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.machineManager.core import saveData

# ==== global ==== #
TEXT_FIELD_TEMPLATE = ("background-color: rgb(85, 85, 85); "
                       "color: rgb({3}, {4}, {5}); "
                       "border: 2px solid rgb({0}, {1}, {2})")
DEFAULT_BACK_GROUND_COLOR = [85, 85, 85]
DEFAULT_TEXT_COLOR = [212, 212, 212]
RED = [value for value in COLORS['red']]


class MachineManager:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.exceptions = []
        self.unfold = False

        self.storeWidget()
        self.connectWidgets()
        applyStyleSheet(self.ui, excluded=self.exceptions)
        self.initializeUi()

    def storeWidget(self):
        self.uiMenus = self.ui.uiMenus

        self.nameField = self.ui.nameField
        self.infoLayout = self.ui.infoLayout
        self.endButton = self.ui.endButton
        self.infoLine = self.ui.infoLine
        self.commentButton = self.ui.commentButton
        self.exceptions.append(self.commentButton)
        self.commentField = self.ui.commentField
        self.widgets = [w for w in self.uiMenus.get('neededInfo', {}).values() if isinstance(w, QtWidgets.QLineEdit)]

    def connectWidgets(self):
        self.commentButton.clicked.connect(partial(self.foldCommand))
        self.endButton.clicked.connect(partial(self.saveNewMachineInfo))
        for widget in self.widgets:
            widget.textChanged.connect(lambda _: self.checkGivenInfo())
        self.nameField.textChanged.connect(partial(self.checkGivenInfo))

    def checkGivenInfo(self, *args):
        machineData = getMachineData()
        machineName = self.nameField.text()
        if not machineName:
            self.manageNameField(True)
            self.endButton.setEnabled(False)
            return

        if machineName and machineName.lower() in [x.lower() for x in machineData.keys()]:
            self.manageNameField(False)
            self.endButton.setEnabled(False)
            return

        self.manageNameField(True)
        missingInfos = [widget for widget in self.widgets if not widget.text()]
        self.endButton.setEnabled(missingInfos == [])

    def manageNameField(self, value):
        color = DEFAULT_BACK_GROUND_COLOR if value else RED
        color.extend(DEFAULT_TEXT_COLOR if value else RED)
        self.nameField.setStyleSheet(TEXT_FIELD_TEMPLATE.format(*color))

        self.infoLine.setVisible(not value)

        if value:
            self.ui.adjustSize()
            return

        machineName = self.nameField.text()
        self.infoLine.setText(f'{machineName} even exists in data')
        self.infoLine.setStyleSheet("color: rgb({3}, {4}, {5});".format(*RED))

    def saveNewMachineInfo(self, *args):
        machineName = self.nameField.text()

        machineData = {}
        for name, widget in self.uiMenus.get('neededInfo', {}).items():
            if isinstance(widget, QtWidgets.QComboBox):
                value = widget.currentText()

            elif isinstance(widget, QtWidgets.QLineEdit):
                value = widget.text()

            else:
                continue

            machineData[name] = value

        machineData['comment'] = self.commentField.toPlainText() or ''

        saveData(machineName, machineData)
        self.ui.close()

    def foldCommand(self, *args):
        text = '-  commentaire' if self.unfold else '⬐ commentaire'
        self.unfold = not self.unfold
        self.commentButton.setText(text)
        self.commentField.setVisible(self.unfold)
        self.ui.adjustSize()

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