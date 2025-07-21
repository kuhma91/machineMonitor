"""
===============================================================================
fileName: machineMonitor.machineManager.ui
scripter: angiu
creation date: 18/07/2025
description:
===============================================================================
"""
# ==== native ==== #
import os

# ==== third ==== #
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

# ==== local ===== #
from machineMonitor.library.general.stringLib import formatString
from machineMonitor.library.general.infoLib import COLORS
from machineMonitor.machineManager.core import NEEDED_INFOS
from machineMonitor.machineManager.core import ICON_FOLDER
from machineMonitor.machineManager.core import BUTTONS

# ==== global ==== #


class MachineManagerUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MachineManagerUi, self).__init__(parent)
        self.uiName = formatString(__class__.__name__.split('Ui')[0])

        self.uiWidth = 450
        self.uiMenus = {}
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.uiName)
        self.setMinimumWidth(self.uiWidth + 45)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        nameLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('machine name : ')
        label.setMinimumSize(self.uiWidth // 4, 20)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        nameLayout.addWidget(label)

        self.nameBox = QtWidgets.QComboBox()
        self.nameBox.setMinimumSize((self.uiWidth // 4) * 3, 20)
        self.nameBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        nameLayout.addWidget(self.nameBox)

        self.nameField = QtWidgets.QLineEdit()
        self.nameField.setMinimumSize((self.uiWidth // 4) * 3, 20)
        self.nameField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.nameField.setVisible(False)
        nameLayout.addWidget(self.nameField)

        for name in BUTTONS:
            button = QtWidgets.QPushButton()
            button.setMinimumSize(20, 20)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            button.setIcon(QIcon(os.path.join(ICON_FOLDER, f'{name}.png')))
            nameLayout.addWidget(button)

        nameLayout.setStretch(0, 1)
        nameLayout.setStretch(1, 3)
        nameLayout.setStretch(2, 3)

        self.mainLayout.addLayout(nameLayout)

        self.infoLine = QtWidgets.QLabel()
        self.infoLine.setMinimumSize(self.uiWidth, 20)
        self.infoLine.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.infoLine.setAlignment(Qt.AlignCenter)
        self.infoLine.setVisible(False)
        self.mainLayout.addWidget(self.infoLine)

        spacer = QtWidgets.QSpacerItem((self.uiWidth // 4) * 3, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        self.infoLayout = QtWidgets.QVBoxLayout()
        for name, defaultValue in NEEDED_INFOS.items():
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f'{name} : ')
            label.setMinimumSize(self.uiWidth // 3, 20)
            label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            layout.addWidget(label)

            if isinstance(defaultValue, list) or isinstance(defaultValue, bool):
                widget = QtWidgets.QComboBox()
                if isinstance(defaultValue, list):
                    widget.addItems(sorted(defaultValue))
                else:
                    widget.addItems(['Oui', 'Non'])
            else:
                widget = QtWidgets.QLineEdit()
                if defaultValue:
                    widget.setText(str(defaultValue))

            widget.setMinimumSize((self.uiWidth // 3) * 2, 20)
            widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            widget.setEnabled(False)
            layout.addWidget(widget)
            layout.setStretch(0, 1)
            layout.setStretch(1, 2)

            self.infoLayout.addLayout(layout)
            self.uiMenus.setdefault('neededInfo', {})[name] =  widget

        self.mainLayout.addLayout(self.infoLayout)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        layout = QtWidgets.QHBoxLayout()
        self.commentButton = QtWidgets.QPushButton(f'-  commentaire')
        self.commentButton.setMinimumSize(self.uiWidth // 4, 20)
        self.commentButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.commentButton.setFlat(True)
        self.commentButton.setStyleSheet("background:transparent; border:none; color: rgb(212, 212, 212);")
        layout.addWidget(self.commentButton)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        line.setLineWidth(1)
        line.setStyleSheet("background-color: black;")
        layout.addWidget(line)

        self.mainLayout.addLayout(layout)

        self.commentField = QtWidgets.QTextEdit()
        self.commentField.setMinimumSize(self.uiWidth, 250)
        self.commentField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.commentField.setVisible(False)
        self.mainLayout.addWidget(self.commentField)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        self.endContainer = QtWidgets.QWidget()
        self.endContainer.setVisible(False)

        layout = QtWidgets.QHBoxLayout(self.endContainer)
        spacer = QtWidgets.QLabel('')
        spacer.setMinimumSize((self.uiWidth // 4) * 2, 20)
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(spacer)

        self.endButton = QtWidgets.QPushButton('   save')
        self.endButton.setMinimumSize(self.uiWidth // 4, 20)
        self.endButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.endButton.setIcon(QIcon(os.path.join(ICON_FOLDER, f'save.png')))
        self.endButton.setEnabled(False)
        layout.addWidget(self.endButton)

        layout.setStretch(0, 3)
        layout.setStretch(1, 1)
        self.mainLayout.addWidget(self.endContainer)


