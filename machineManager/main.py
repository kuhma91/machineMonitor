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
from PyQt5 import QtWidgets

# ==== local ===== #
from machineMonitor.library.uiLib import applyStyleSheet
from machineMonitor.library.uiLib import loadUi
from machineMonitor.library.uiLib import confirmDialog
from machineMonitor.library.infoLib import COLORS
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.machineManager.core import addEntry
from machineMonitor.machineManager.core import deleteEntry

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
        self.mode = 'read'

        self.storeWidget()
        self.connectWidgets()
        self.fillUi()
        applyStyleSheet(self.ui, excluded=self.exceptions)
        self.initializeUi()

    def storeWidget(self):
        self.uiMenus = self.ui.uiMenus

        self.nameField = self.ui.nameField
        self.nameBox = self.ui.nameBox
        self.infoLayout = self.ui.infoLayout
        self.endButton = self.ui.endButton
        self.cancelButton = self.ui.cancelButton
        self.infoLine = self.ui.infoLine
        self.commentButton = self.ui.commentButton
        self.exceptions.append(self.commentButton)
        self.commentField = self.ui.commentField
        self.endContainer = self.ui.endContainer
        self.widgets = [w for w in self.uiMenus.get('neededInfo', {}).values() if isinstance(w, QtWidgets.QLineEdit)]

    def fillUi(self, machine=None, *args):
        machineData = getMachineData()

        self.nameBox.blockSignals(True)
        self.nameBox.clear()
        machines = sorted(list(machineData.keys()))
        self.nameBox.addItems(machines)

        if machine and machine in machines:
            self.nameBox.setCurrentText(machine)

        self.updateField()
        self.nameBox.blockSignals(False)

    def connectWidgets(self):
        self.commentButton.clicked.connect(partial(self.foldCommand))
        self.endButton.clicked.connect(partial(self.saveNewMachineInfo))
        self.nameField.textChanged.connect(partial(self.checkGivenInfo))
        self.nameBox.currentTextChanged.connect(partial(self.updateField))
        self.cancelButton.clicked.connect(partial(self.cancelCommand))

        for widget in self.widgets:
            widget.textChanged.connect(lambda _: self.checkGivenInfo())

        for name, button in self.uiMenus.get('optionButton', {}).items():
            button.clicked.connect(partial(self.optionCommand, name))

    def cancelCommand(self, *args):
        currentName = self.nameBox.currentText() if self.mode == 'edit' else None
        self.restartUi(currentName)

    def restartUi(self, name=None):
        self.endContainer.setVisible(False)
        self.endButton.setEnabled(False)
        self.cancelButton.setVisible(False)
        self.nameBox.setVisible(True)
        self.nameBox.setEnabled(True)
        self.nameField.setVisible(False)
        self.nameField.setText('')
        for widget in self.uiMenus.get('neededInfo', {}).values():
            widget.setEnabled(False)

        self.mode = 'read'

        self.fillUi(machine=name)

    def optionCommand(self, toDo, *args):
        selected = self.nameBox.currentText()
        if toDo == 'delete':
            answer = confirmDialog(f'are you sure you want to delete: {selected}')
            if not answer:
                return

            deleteEntry(selected)
            self.restartUi()

        elif toDo == 'edit':
            self.mode = 'edit'
            self.nameBox.setVisible(True)
            self.nameBox.setEnabled(False)
            self.nameField.setVisible(False)
            self.endContainer.setVisible(True)
            self.endButton.setText('   save')
            self.endButton.setEnabled(True)
            self.cancelButton.setVisible(True)
            for widget in self.uiMenus.get('neededInfo', {}).values():
                widget.setEnabled(True)

        else:
            self.mode = 'add'
            self.nameBox.setEnabled(False)
            self.nameBox.setVisible(False)
            self.nameField.setVisible(True)
            self.nameField.setEnabled(True)
            self.endContainer.setVisible(True)
            self.endButton.setText('   create')
            self.endButton.setEnabled(False)
            self.nameField.clear()
            for widget in self.uiMenus.get('neededInfo', {}).values():
                widget.setEnabled(True)

            for widget in self.widgets:
                widget.clear()

            self.commentField.clear()

    def updateField(self, *args):
        machineData = getMachineData()
        machine = self.nameBox.currentText()
        data = machineData[machine]

        for name, widget in self.uiMenus.get('neededInfo', {}).items():
            value = data[name]
            if isinstance(widget, QtWidgets.QComboBox):
                widget.setCurrentText(value)
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.setText(value)

        comment = data['comment']
        self.commentField.setText(comment)

    def checkGivenInfo(self, *args):
        machineData = getMachineData()
        machineName = self.nameField.text()
        if machineName and machineName.lower() in [x.lower() for x in machineData.keys()]:
            self.manageNameField(False)
            self.endButton.setEnabled(False)

        else:
            self.manageNameField(True)
            if not machineName:
                self.endButton.setEnabled(False)

        missingInfos = [widget for widget in self.widgets if not widget.text()]
        self.endButton.setEnabled(missingInfos == [])

    def manageNameField(self, value):
        if value or self.mode == 'edit':
            color = DEFAULT_BACK_GROUND_COLOR
            color.extend(DEFAULT_TEXT_COLOR)
        else:
            color = RED
            color.extend(RED)

        self.nameField.setStyleSheet(TEXT_FIELD_TEMPLATE.format(*color))
        visibleValue = False if self.mode == 'edit' else not value
        self.infoLine.setVisible(visibleValue)

        if value:
            self.ui.adjustSize()
            return

        machineName = self.nameField.text()
        self.infoLine.setText(f'{machineName} even exists in data')
        self.infoLine.setStyleSheet("color: rgb({3}, {4}, {5});".format(*color))

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

        addEntry(machineName, machineData)
        self.restartUi(machineName)

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