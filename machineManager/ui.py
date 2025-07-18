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
from PySide2.QtGui import QIcon

# ==== local ===== #
from machineMonitor.library.general.stringLib import formatString
from machineMonitor.machineManager.core import NEEDED_INFOS
from machineMonitor.machineManager.core import ICON_FOLDER

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
        label = QtWidgets.QLabel('name')
        label.setMinimumSize(self.uiWidth // 4, 20)
        label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        nameLayout.addWidget(label)

        self.nameField = QtWidgets.QLineEdit()
        self.nameField.setMinimumSize((self.uiWidth // 4) * 3, 20)
        self.nameField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        nameLayout.addWidget(self.nameField)
        nameLayout.setStretch(0, 1)
        nameLayout.setStretch(1, 3)

        self.mainLayout.addLayout(nameLayout)

        self.infoLine = QtWidgets.QLineEdit()
        self.infoLine.setMinimumSize(self.uiWidth, 20)
        self.infoLine.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.infoLine.setVisible(False)
        self.mainLayout.addWidget(self.infoLine)

        spacer = QtWidgets.QSpacerItem((self.uiWidth // 4) * 3, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        self.infoLayout = QtWidgets.QVBoxLayout()

        for name, defaultValue in NEEDED_INFOS.items():
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(name)
            label.setMinimumSize(self.uiWidth // 3, 20)
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
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
            layout.addWidget(widget)
            layout.setStretch(0, 1)
            layout.setStretch(1, 2)

            self.infoLayout.addLayout(layout)
            self.uiMenus.setdefault('neededInfo', {})[name] = widget

        self.mainLayout.addLayout(self.infoLayout)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        layout = QtWidgets.QHBoxLayout()
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

        self.mainLayout.addLayout(layout)
        layout.setStretch(0, 3)
        layout.setStretch(1, 1)


