"""
===============================================================================
fileName: machineMonitor.logger.ui
scripter: angiu
creation date: 22/07/2025
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


class MachineMonitorLoggerUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MachineMonitorLoggerUi, self).__init__(parent)
        self.uiName = formatString(__class__.__name__.split('Ui')[0])

        self.uiWidth = 250
        self.uiMenus = {}
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.uiName)
        self.setMinimumWidth(self.uiWidth + 45)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
