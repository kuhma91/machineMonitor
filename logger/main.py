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
from functools import partial

# ==== third ==== #
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

# ==== local ===== #
from machineMonitor.library.uiLib import applyStyleSheet
from machineMonitor.library.uiLib import deleteLayout
from machineMonitor.library.uiLib import confirmDialog
from machineMonitor.library.uiLib import loadUi
from machineMonitor.library.uiLib import STYLE_SHEET
from machineMonitor.machineManager.core import getMachineData
from machineMonitor.logger.core import LOG_TYPES
from machineMonitor.logger.core import getInitInfo
from machineMonitor.logger.core import ICON_FOLDER
from machineMonitor.logger.core import NO_MACHINE_CMD
from machineMonitor.logger.core import EXCLUDED_KEYS
from machineMonitor.logger.core import saveData
from machineMonitor.logger.core import clearTempData
from machineMonitor.logger.core import getCompleterData
from machineMonitor.logger.core import getTableWidgetData
from machineMonitor.logger.core import deleteLogs
from machineMonitor.logger.core import getDataFromUuid

# ==== global ==== #


class Logger:
    def __init__(self, logUuid=None, asDialog=False):
        self.ui = loadUi(__file__, __class__.__name__, asDialog=asDialog)

        self.uiMenus = self.ui.uiMenus
        self.logUuid = logUuid

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

        if not self.logUuid:
            filePath, data, fromError = getInitInfo()
            if not filePath:
                return

            if not fromError:
                choice = confirmDialog(message='temp file found ! do you want to load it ?')
                if not choice:
                    return

            if fromError:
                os.remove(filePath)
                return

            self.fromTemp = filePath

        else:
            data = getDataFromUuid(self.logUuid)

        self.machineBox.setCurrentText(data.get('machineName', ''))
        self.logBox.setCurrentText(data.get('type'))
        self.projectField.setText(data.get('project', ''))
        self.commentField.setPlainText(data.get('comment', ''))

        self.endButton.setEnabled(True)

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

        result = saveData(data, mode='temp' if not machine else 'save', logUuid=None if not machine else self.logUuid)
        if result:
            choice = confirmDialog(message=f'fail while saving data: {result} ! do you want to backup ?')
            if not choice:
                return

            result = saveData(data, mode='backup')
            if result:
                print(f'fail to backup: {result}')

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

        self.saveButton = False
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
        self.tableWidget = self.ui.tableWidget

    def fillUi(self):
        self.fillCompleter()
        self.fillTable()

    def connectWidgets(self):
        self.filterField.textChanged.connect(self.checkEntry)
        self.popup.clicked.connect(self.fillFieldFromCompleter)
        self.filterButton.clicked.connect(self.addFilter)
        self.tableWidget.cellClicked.connect(self.onCellSelected)
        for name, button in self.uiMenus.get('sideButtons', {}).items():
            button.clicked.connect(partial(self.sideCommand, name))

    def getUuiFromTableSelection(self):
        row = self.tableWidget.currentRow()
        col = next(i for i in range(self.tableWidget.columnCount()) if self.tableWidget.horizontalHeaderItem(i).text() == 'uuid')
        return self.tableWidget.item(row, col).text()

    def sideCommand(self, action, *args):
        logUuid = self.getUuiFromTableSelection()
        if action == 'delete':
            choice = confirmDialog(f'are you sure you wante to delete: {logUuid} ?')
            if not choice:
                return

            value = deleteLogs(logUuid)
            if not value:
                print(f'error deleting: {logUuid} -> {value}')
                return

        else:
            Logger(asDialog=True, logUuid=logUuid)

        self.fillUi()

    def onCellSelected(self, *args):
        selected = self.getUuiFromTableSelection()
        for name, button in self.uiMenus.get('sideButtons', {}).items():
            button.setToolTip(f'{name}: {selected}')
            button.setEnabled(True)

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

    def fillTable(self, startup=False, *args):
        tableData = getTableWidgetData(list(self.uiMenus.get('filter', {}).keys()))

        headers = list(set([x for info in tableData for x in info.keys() if x not in EXCLUDED_KEYS]))

        self.tableWidget.clearContents()

        # build header
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        self.tableWidget.setRowCount(len(tableData))

        # fill cells
        for rowIndex, data in enumerate(tableData):
            for columnIndex, key in enumerate(headers):
                item = QtWidgets.QTableWidgetItem(str(data[key]))
                item.setTextAlignment(Qt.AlignCenter)  # Center text horizontally and vertically
                if key == 'machineName':
                    toolTip = '\n'.join(f'{k}: {v}' for k, v in data['machineData'].items())
                elif key == 'date':
                    toolTip = data['timeStamp']
                elif key == 'type':
                    toolTip = data['comment']
                elif key == 'modified':
                    toolTip = '\n'.join('modified by: {0} at: {1}'.format(*x) for x in data[key])
                else:
                    toolTip = data[key]

                item.setToolTip(toolTip)

                self.tableWidget.setItem(rowIndex, columnIndex, item)

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