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
from machineMonitor.library.general.uiLib import deleteLayout
from machineMonitor.library.general.uiLib import confirmDialog
from machineMonitor.library.general.uiLib import loadUi
from machineMonitor.library.general.uiLib import STYLE_SHEET
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.logger.core import LOG_TYPES
from machineMonitor.logger.core import getInitInfo
from machineMonitor.logger.core import ICON_FOLDER
from machineMonitor.logger.core import NO_MACHINE_CMD
from machineMonitor.logger.core import saveData
from machineMonitor.logger.core import clearTempData
from machineMonitor.logger.core import getCompleterData
from machineMonitor.logger.core import getTableWidgetData

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

        filePath, data, fromError = getInitInfo()
        if not filePath:
            return

        if not fromError:
            choice = confirmDialog(message='temp file found ! do you want to load it ?')
            if not choice:
                return

        self.machineBox.setCurrentText(data.get('machineName', ''))
        self.logBox.setCurrentText(data.get('type'))
        self.projectField.setText(data.get('project', ''))
        self.commentField.setPlainText(data.get('comment', ''))

        self.endButton.setEnabled(True)

        if fromError:
            os.remove(filePath)
            return

        self.fromTemp = filePath

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

        result = saveData(data, mode='temp' if not machine else 'save')
        if result:
            choice = confirmDialog(message=f'fail while saving data : {result} ! do you want to backup ?')
            if not choice:
                return

            result = saveData(data, mode='backup')
            if result:
                print(f'fail to backup : {result}')

        if self.fromTemp:
            os.remove(self.fromTemp)

        self.ui.close()

    def initializeUi(self, *args):
        if QtWidgets.QApplication.instance() is None:
                self.app = QtWidgets.QApplication(sys.argv)
        else:
            self.app = QtWidgets.QApplication.instance()

        if isinstance(self.ui, QtWidgets.QDialog):
            self.ui.exec_()
        else:
            self.ui.show()


class LogViewer:
    def __init__(self, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.uiMenus = self.ui.uiMenus

        self.completionList = getCompleterData()
        clearTempData()

        self.storeWidget()
        self.fillUi()
        self.connectWidgets()
        applyStyleSheet(self.ui, excluded=self.uiMenus.get('excluded', []))
        self.initializeUi()

    def storeWidget(self):
        self.model = self.ui.model
        self.filterField = self.ui.filterField
        self.completer = self.ui.completer
        self.popup = self.completer.popup()
        self.filterButton = self.ui.filterButton
        self.scorllContainer = self.ui.scorllContainer
        self.scrollLayout = self.ui.scrollLayout

    def fillUi(self):
        self.fillCompleter()

    def connectWidgets(self):
        self.filterField.textChanged.connect(self.checkEntry)
        self.popup.clicked.connect(self.fillFieldFromCompleter)
        self.filterButton.clicked.connect(self.addFilter)

    def checkEntry(self):
        entry = self.filterField.text()
        if entry not in [x for v in self.completionList.values() for x in v]:
            value = False
        else:
            value = True

        self.filterButton.setEnabled(value)

    def fillFieldFromCompleter(self, index):
        selected = index.data()
        self.filterField.setText(selected.split('[')[0].strip())

    def addFilter(self, *args):
        self.scorllContainer.setVisible(True)
        entry = self.filterField.text()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        layout.setSpacing(0)  # Remove spacing between widgets

        label = QtWidgets.QPushButton(entry)
        label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(label)

        button = QtWidgets.QPushButton('x')
        button.setMinimumSize(20, 20)
        button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        button.clicked.connect(partial(self.removeFilter, entry))
        layout.addWidget(button)

        applyStyleSheet(widgets=[label, button])

        self.scrollLayout.addLayout(layout)
        self.scrollLayout.addStretch()

        self.uiMenus.setdefault('excluded', []).append(entry)
        self.uiMenus.setdefault('filter', {})[entry] = layout

        self.fillTable()

    def removeFilter(self, name, *args):
        excluded = self.uiMenus.get('excluded', [])
        excluded.remove(name)
        self.uiMenus['excluded'] = excluded

        filters = self.uiMenus.get('filter', {})
        layout = filters.get(name)
        deleteLayout(layout)


        del filters[name]
        self.uiMenus['filter'] = filters

        if not filters:
            self.scorllContainer.setVisible(False)

        self.fillTable()

    def fillTable(self, *args):
        tableData = getTableWidgetData(list(self.uiMenus.get('filter').keys()))
        import pprint
        pprint.pprint(tableData)


    def fillCompleter(self, *args):
        self.completionList = getCompleterData(excluded=self.uiMenus.get('excluded', []))
        self.model.setStringList([])
        self.model.setStringList([f'{x} [{k}]' for k, v in self.completionList.items() for x in v])

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
    LogViewer()