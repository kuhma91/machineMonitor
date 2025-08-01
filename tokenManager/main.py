"""
===============================================================================
fileName: machineMonitor.tokenManager.main
scripter: angiu
creation date: 01/08/2025
description: 
===============================================================================
"""
# ==== native ==== #
import sys
from copy import deepcopy
from functools import partial

# ==== third ==== #
from PySide2 import QtWidgets

# ==== local ===== #
from machineMonitor.library.general.uiLib import applyStyleSheet
from machineMonitor.library.general.uiLib import loadUi
from machineMonitor.tokenManager.core import AUTHORISATIONS
from machineMonitor.tokenManager.core import generateToken
from machineMonitor.tokenManager.core import generateTrigram
from machineMonitor.tokenManager.core import getUsers
from machineMonitor.tokenManager.core import saveData

# ==== global ==== #


class TokenManager:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.uiMenus = self.ui.uiMenus

        self.storeWidget()
        self.fillUi()
        self.connectWidgets()
        applyStyleSheet(self.ui)
        self.initializeUi()

    def storeWidget(self):
        self.nameContainer = self.ui.nameContainer
        self.userContainer = self.ui.userContainer
        self.endContainer = self.ui.endContainer
        self.nameBox = self.ui.nameBox
        self.authorisationBox = self.ui.authorisationBox

    def fillUi(self):
        users = getUsers()
        self.nameBox.clear()
        self.nameBox.addItems(sorted(list(users.keys())))

        self.authorisationBox.clear()
        self.authorisationBox.addItems(sorted(AUTHORISATIONS))

        self.nameBoxCommand()

    def connectWidgets(self):
        self.nameBox.currentTextChanged.connect(self.nameBoxCommand)
        for name, button in self.uiMenus.get('sideButtons', {}).items():
            button.clicked.connect(partial(self.sideButtonCommand, name))

        for name, button in self.uiMenus.get('endMenus', {}).items():
            button.clicked.connect(partial(self.endButtonCommand, name))

        for name, info in self.uiMenus.get('infoField', {}).items():
            button = info.get('button')
            if not button:
                continue

            button.clicked.connect(partial(self.infoButtonCommand, name))

        for name, textField in self.uiMenus.get('nameField', {}).items():
            textField.textChanged.connect(partial(self.nameChangedCommand, name))

    def nameChangedCommand(self, name, *args):
        nameWidgets = self.uiMenus.get('nameField', {})

        nameDict = {}
        for k, textField in nameWidgets.items():
            entry = textField.text().strip()
            if not entry:
                break

            nameDict[k] = entry.strip()

        value = False
        if len(nameDict) == len(nameWidgets):
            users = getUsers()
            value = ' '.join(nameDict) not in users

        trigram = None
        if value:
            trigram = generateTrigram(**nameDict)
            value = trigram is not None

        if value:
            self.uiMenus.get('infoField', {}).get('trigram', {}).get('textField').setText(trigram)

        self.uiMenus.get('endMenus', {}).get('save').setEnabled(value)

    def infoButtonCommand(self, name, *args):
        token = generateToken()
        self.uiMenus.get('infoField', {}).get('token', {}).get('textField').setText(token)

    def endButtonCommand(self, name, *args):
        users = getUsers()
        nameValue = ' '.join([x.text().strip().lower() for x in self.uiMenus.get('nameField', {}).values()]).strip()
        if nameValue in users:
            self.nameBox.setCurrentText(nameValue)

        for info in self.uiMenus.get('infoField', {}).values():
            button = info['button']
            if not button:
                continue

            button.setVisible(False)

        if not nameValue:
            self.authorisationBox.setCurrentText(min(AUTHORISATIONS))

        if name == 'save' and nameValue:
            data = {k: v.text() for k, v in self.uiMenus.get('nameField', {}).items()}
            data.update({k: v['textField'].text() for k, v in self.uiMenus.get('infoField', {}).items()})
            data['authorisation'] = self.authorisationBox.currentText()
            saveData(nameValue, data)

        self.nameContainer.setVisible(False)
        self.endContainer.setVisible(False)
        self.userContainer.setVisible(True)
        self.authorisationBox.setEnabled(False)

        if name == 'save':
            self.fillUi()
            self.nameBox.setCurrentText(nameValue)

        self.ui.adjustSize()

    def nameBoxCommand(self):
        currentUser = self.nameBox.currentText()
        users = getUsers()
        data = users.get(currentUser, {})

        for name, info in self.uiMenus.get('infoField', {}).items():
            info['textField'].setText(data.get(name, ''))

        for i, (name, textField) in enumerate(self.uiMenus.get('nameField', {}).items()):
            textField.setText(currentUser.split(' ')[i] if currentUser else '')

        self.authorisationBox.setCurrentText(data.get('authorisation', min(AUTHORISATIONS)))

    def sideButtonCommand(self, name, *args):
        if name == 'edit':
            user = self.nameBox.currentText()
            nameFieldInfo = self.uiMenus.get('nameField', {})
            data = {name: user.split(' ')[i] if user else '' for i, name in enumerate(nameFieldInfo.keys())}
            for name, textField in nameFieldInfo.items():
                textField.setText(data[name])

            self.uiMenus.get('endMenus', {}).get('save').setEnabled(True)

        elif name == 'add':
            for textField in self.uiMenus.get('nameField', {}).values():
                textField.clear()

            for info in self.uiMenus.get('infoField', {}).values():
                info.get('textField').clear()

            self.authorisationBox.setCurrentText(min(AUTHORISATIONS))

        for info in self.uiMenus.get('infoField', {}).values():
            button = info['button']
            if not button:
                continue

            button.setVisible(True)

        self.nameContainer.setVisible(True)
        self.endContainer.setVisible(True)
        self.userContainer.setVisible(False)
        self.authorisationBox.setEnabled(True)

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
    TokenManager()