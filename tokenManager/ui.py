"""
===============================================================================
fileName: machineMonitor.tokenManager.ui
scripter: angiu
creation date: 01/08/2025
description:
===============================================================================
"""
# ==== native ==== #
import os

# ==== third ==== #
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

# ==== local ===== #
from machineMonitor.library.stringLib import formatString
from machineMonitor.tokenManager.core import ICON_FOLDER

# ==== global ==== #


class TokenManagerUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TokenManagerUi, self).__init__(parent)
        self.uiName = formatString(__class__.__name__.split('Ui')[0])

        self.uiWidth = 400
        self.uiMenus = {}
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.uiName)
        self.setMinimumWidth(self.uiWidth + 45)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        self.nameContainer = QtWidgets.QWidget()
        self.nameContainer.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QHBoxLayout(self.nameContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        for nameLabel in ['firstName', 'lastName']:
            label = QtWidgets.QLabel(nameLabel)
            label.setMinimumSize(self.uiWidth // 8, 25)
            label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            layout.addWidget(label)

            textField = QtWidgets.QLineEdit()
            textField.setMinimumSize((self.uiWidth // 8) * 3, 25)
            textField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            layout.addWidget(textField)

            self.uiMenus.setdefault('nameField', {})[nameLabel] = textField

        self.nameContainer.setVisible(False)
        self.mainLayout.addWidget(self.nameContainer)

        self.userContainer = QtWidgets.QWidget()
        self.userContainer.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QHBoxLayout(self.userContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel('user: ')
        label.setMinimumSize(self.uiWidth // 4, 25)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(label)

        self.nameBox = QtWidgets.QComboBox()
        self.nameBox.setMinimumSize(((self.uiWidth // 4) * 3) - 50, 25)
        self.nameBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(self.nameBox)

        for name in ['edit', 'add']:
            button = QtWidgets.QPushButton('')
            button.setMinimumSize(25, 25)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            button.setIcon(QIcon(os.path.join(ICON_FOLDER, f'{name}.png')))
            button.setToolTip(name)
            layout.addWidget(button)

            self.uiMenus.setdefault('sideButtons', {})[name] = button

        self.mainLayout.addWidget(self.userContainer)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel('authorisation: ')
        label.setMinimumSize(self.uiWidth // 4, 25)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(label)

        self.authorisationBox = QtWidgets.QComboBox()
        self.authorisationBox.setMinimumSize(((self.uiWidth // 4) * 3), 25)
        self.authorisationBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.authorisationBox.setEnabled(False)
        layout.addWidget(self.authorisationBox)

        self.mainLayout.addLayout(layout)

        for i, name in enumerate(['trigram', 'token']):
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f'{name}: ')
            label.setMinimumSize(self.uiWidth // 4, 25)
            label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            layout.addWidget(label)

            textField = QtWidgets.QLineEdit()
            textField.setMinimumSize(((self.uiWidth // 4) * 3) - 25, 25)
            textField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            textField.setEnabled(False)
            layout.addWidget(textField)

            button = None
            if name == 'token':
                button = QtWidgets.QPushButton('')
                button.setMinimumSize(25, 25)
                button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                button.setIcon(QIcon(os.path.join(ICON_FOLDER, f'generate.png')))
                button.setToolTip(f'generate new {name}')
                button.setVisible(False)
                layout.addWidget(button)

            self.uiMenus.setdefault('infoField', {})[name] = {'textField': textField, 'button': button}

            self.mainLayout.addLayout(layout)

            if i == 1:
                spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
                self.mainLayout.addItem(spacer)

        self.endContainer = QtWidgets.QWidget()
        self.endContainer.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QHBoxLayout(self.endContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        spacer = QtWidgets.QSpacerItem((self.uiWidth // 4) * 3, 25, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)

        for name in ['cancel', 'save']:
            button = QtWidgets.QPushButton('')
            button.setMinimumSize((self.uiWidth // 4) // 2, 25)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            button.setIcon(QIcon(os.path.join(ICON_FOLDER, f'{name}.png')))
            button.setToolTip(f'{name}')
            if name == 'save':
                button.setEnabled(False)

            layout.addWidget(button)

            self.uiMenus.setdefault('endMenus', {})[name] = button

        self.endContainer.setVisible(False)

        self.mainLayout.addWidget(self.endContainer)
