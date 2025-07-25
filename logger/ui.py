"""
===============================================================================
fileName: machineMonitor.logger.ui
scripter: angiu
creation date: 22/07/2025
description:
===============================================================================
"""
# ==== native ==== #
import os

# ==== third ==== #
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

# ==== local ===== #
from machineMonitor.library.general.stringLib import formatString
from machineMonitor.logger.core import NO_MACHINE_CMD
from machineMonitor.logger.core import ICON_FOLDER
from machineMonitor.logger.core import R, G, B

# ==== global ==== #


class LoggerUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoggerUi, self).__init__(parent)
        self.uiName = formatString(__class__.__name__.split('Ui')[0])

        self.uiWidth = 400
        self.uiMenus = {}
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.uiName)
        self.setMinimumWidth(self.uiWidth + 45)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('machine name : ')
        label.setMinimumSize(self.uiWidth // 4, 20)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(label)

        self.machineBox = QtWidgets.QComboBox()
        self.machineBox.setMinimumSize(((self.uiWidth // 4) * 3) - 50, 20)
        self.machineBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.machineBox.setStyleSheet(NO_MACHINE_CMD)
        self.uiMenus.setdefault('excluded', []).append(self.machineBox)
        layout.addWidget(self.machineBox)

        # buttons = AUTHORISATIONS.get(getAuthorisation(), [])
        # for name in buttons:
        #     button = QtWidgets.QPushButton('')
        #     button.setMinimumSize(20, 20)
        #     button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        #     button.setIcon(QIcon(os.path.join(ICON_FOLDER, f'{name}.png')))
        #     button.setToolTip(name)
        #     self.uiMenus.setdefault('optionButtons', {})[name] = button
        #     layout.addWidget(button)

        self.mainLayout.addLayout(layout)

        self.infoLine = QtWidgets.QLabel('Machine not listed? temp Save and notify your supervisor.')
        self.infoLine.setMinimumSize(self.uiWidth, 20)
        self.infoLine.setMinimumSize(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.infoLine.setAlignment(Qt.AlignCenter)
        self.infoLine.setStyleSheet(f"QLabel {{ color: rgb({R}, {G}, {B}); }}")
        self.uiMenus.setdefault('excluded', []).append(self.infoLine)
        self.mainLayout.addWidget(self.infoLine)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('log type : ')
        label.setMinimumSize(self.uiWidth // 4, 20)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(label)

        self.logBox = QtWidgets.QComboBox()
        self.logBox.setMinimumSize((self.uiWidth // 4) * 3, 20)
        self.logBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(self.logBox)

        self.mainLayout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('project Id : ')
        label.setMinimumSize(self.uiWidth // 4, 20)
        label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(label)

        self.projectField = QtWidgets.QLineEdit()
        self.projectField.setMinimumSize((self.uiWidth // 4) * 3, 20)
        self.projectField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(self.projectField)

        self.mainLayout.addLayout(layout)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 30, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        layout = QtWidgets.QHBoxLayout()
        self.commentButton = QtWidgets.QPushButton(f'commentaire   ')
        self.commentButton.setMinimumSize(self.uiWidth // 4, 20)
        self.commentButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.commentButton.setFlat(True)
        self.commentButton.setStyleSheet("background:transparent; border:none; color: rgb(212, 212, 212);")
        self.commentButton.setIcon(QIcon(os.path.join(ICON_FOLDER, 'folded.png')))
        self.commentButton.setLayoutDirection(Qt.RightToLeft)
        self.uiMenus.setdefault('excluded', []).append(self.commentButton)
        layout.addWidget(self.commentButton)

        spacer = QtWidgets.QSpacerItem((self.uiWidth // 4) * 3, 30, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)

        self.mainLayout.addLayout(layout)

        self.commentField = QtWidgets.QTextEdit()
        self.commentField.setMinimumSize(self.uiWidth, 250)
        self.commentField.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.commentField.setVisible(False)
        self.mainLayout.addWidget(self.commentField)

        spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)


        layout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QLabel('')
        spacer.setMinimumSize((self.uiWidth // 4) * 2, 20)
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(spacer)

        self.cancelButton = QtWidgets.QPushButton('   cancel')
        self.cancelButton.setMinimumSize(self.uiWidth // 4, 20)
        self.cancelButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.cancelButton.setIcon(QIcon(os.path.join(ICON_FOLDER, f'cancel.png')))
        self.cancelButton.setVisible(False)
        self.cancelButton.setEnabled(False)
        layout.addWidget(self.cancelButton)

        self.endButton = QtWidgets.QPushButton('   temporary')
        self.endButton.setMinimumSize(self.uiWidth // 4, 20)
        self.endButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.endButton.setIcon(QIcon(os.path.join(ICON_FOLDER, f'save.png')))
        self.endButton.setEnabled(False)
        layout.addWidget(self.endButton)

        layout.setStretch(0, 3)
        layout.setStretch(1, 1)
        self.mainLayout.addLayout(layout)


class LogViewerUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LogViewerUi, self).__init__(parent)
        self.uiName = formatString(__class__.__name__.split('Ui')[0])

        self.uiWidth = 400
        self.uiMenus = {}
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.uiName)
        self.setMinimumWidth(self.uiWidth + 45)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.mainLayout = QtWidgets.QVBoxLayout(self)



