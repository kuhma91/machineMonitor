"""
===============================================================================
fileName: machineMonitor.machineManager.ui
scripter: angiu
creation date: 18/07/2025
description:
===============================================================================
"""
# ==== native ==== #

# ==== third ==== #
from PySide2 import QtWidgets
from PySide2 import QtCore

# ==== local ===== #
from library.general.stringLib import formatString

# ==== global ==== #


class MachineManagerUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MachineManagerUi, self).__init__(parent)
        self.uiName = formatString(__class__.__name__.split('Ui')[0])

        self.uiWidth = 250
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
        label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        nameLayout.addWidget(label)

        self.nameField = QtWidgets.QLineEdit()
        self.nameField.setMinimumSize((self.uiWidth // 4) * 3, 20)
        self.nameField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        nameLayout.addWidget(self.nameField)

        self.mainLayout.addLayout(nameLayout)


