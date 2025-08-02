"""
===============================================================================
fileName: uiLib
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
from functools import partial
import os
import sys
import importlib

# ==== third ==== #
from PySide2.QtCore import Qt
from PySide2 import QtWidgets

# ==== local ===== #

# ==== global ==== #
STYLE_SHEET = {
    'QPushButton': "background-color: rgb(85, 85, 85); color: rgb(212, 212, 212); border: 4px solid rgb(85, 85, 85)",
    'QComboBox': "background-color: rgb(85, 85, 85); color: rgb(212, 212, 212); border: none;",
    'QLabel': "color: rgb(212, 212, 212);",
    'QCheckBox': "color: rgb(212, 212, 212);",
    'QWidget': "background-color: transparent;",
    'QTableWidget': "QTableWidget {background-color: rgb(45, 45, 45); color: rgb(212, 212, 212);} QHeaderView::section { background-color: rgb(85, 85, 85); color: rgb(212, 212, 212);}",
    'QMenuBar': "background-color: transparent; color: rgb(212, 212, 212);",
    'QLineEdit': "background-color: rgb(85, 85, 85); color: rgb(212, 212, 212); border: 4px solid rgb(85, 85, 85)",
    'QTextEdit': "background-color: rgb(85, 85, 85); color: rgb(212, 212, 212); border: 4px solid rgb(85, 85, 85)",
    'QLineEditSpe': "background-color: rgb(45, 45, 45); color: rgb(212, 212, 212); border: 4px solid rgb(45, 45, 45)",
    'QProgressBar': "background-color: rgb(85, 85, 85); color: rgb(212, 212, 212); border: 4px solid rgb(85, 85, 85); text-align: center;",
    'QSplitter': 'QSplitter::handle { background-color: rgb(24, 24, 24); width: 1px; height: 1px; }',
    'QTreeView': 'QHeaderView::section {background-color: rgb(85, 85, 85); color: rgb(212, 212, 212); border: 4px solid rgb(85, 85, 85)} QTreeView {background-color: rgb(85, 85, 85)}'
    }
OTHER_WIDGETS = "background-color: rgb(63, 63, 63); color: rgb(212, 212, 212); border: 4px solid rgb(63, 63, 63)"


def applyStyleSheet(ui=None, widgets=None, excluded=None):
    """
    Apply style sheets to a given UI or list of widgets.

    :param ui: QWidget parent to search widgets from.
    :type ui: QtWidgets.QWidget or None
    :param widgets: List of widgets to apply styles to.
    :type widgets: list[QtWidgets.QWidget] or None
    :param excluded: Set or list of widgets to exclude.
    :type excluded: set[QtWidgets.QWidget] or list or None
    """
    if not ui and not widgets:
        return

    if ui:
        ui.setStyleSheet(f"background-color: rgb(45, 45, 45);")

    if excluded is None:
        excluded = set()

    widgetData = {}
    if not widgets:
        for className in STYLE_SHEET:
            qtClass = getattr(QtWidgets, className, None)
            if not qtClass:
                continue

            for widget in ui.findChildren(qtClass):
                if widget in excluded:
                    continue

                widgetType = widget.__class__.__name__
                widgetData[widget] = STYLE_SHEET.get(widgetType, OTHER_WIDGETS)

    else:
        for widget in widgets:
            if widget in excluded:
                continue

            widgetType = widget.__class__.__name__
            widgetData[widget] = STYLE_SHEET.get(widgetType, OTHER_WIDGETS)

    for widget, style in widgetData.items():
        if widget:
            widget.setStyleSheet(style)


def confirmDialog(message, parent=None):
    class Confirm(QtWidgets.QDialog):
        def __init__(self):
            super().__init__(parent)
            self.setWindowTitle("Prompt")
            self.setModal(True)
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

            self.uiWidth = 150

            self.result = False

            mainLayout = QtWidgets.QVBoxLayout(self)

            label = QtWidgets.QLabel(message)
            label.setMinimumSize(self.uiWidth, 25)
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            mainLayout.addWidget(label)

            spacer = QtWidgets.QSpacerItem(self.uiWidth, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            mainLayout.addItem(spacer)

            layout = QtWidgets.QHBoxLayout()
            spacer = QtWidgets.QSpacerItem((self.uiWidth // 4) * 2, 25, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            layout.addItem(spacer)

            okBtn = QtWidgets.QPushButton("OK")
            okBtn.setMinimumSize(self.uiWidth // 4, 25)
            okBtn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            okBtn.clicked.connect(partial(self.accept, True))
            layout.addWidget(okBtn)

            stopBtn = QtWidgets.QPushButton("Cancel")
            stopBtn.setMinimumSize(self.uiWidth // 4, 25)
            stopBtn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            stopBtn.clicked.connect(partial(self.accept, False))
            layout.addWidget(stopBtn)

            mainLayout.addLayout(layout)

            applyStyleSheet(self)

        def accept(self, value, *args):
            self.result = value
            super().accept()

    dlg = Confirm()
    if dlg.exec_():
        return dlg.result

    return None


def deleteLayout(layout):
    """
    Recursively remove all widgets and sublayouts from the given layout, then delete the layout.

    :param layout: The QLayout to clear and delete.
    :type layout: QLayout
    """
    while layout.count():
        item = layout.takeAt(0)

        if item.widget():
            item.widget().setParent(None)

        elif item.layout():
            deleteLayout(item.layout())

    layout.deleteLater()  # Delete this layout once empty


def loadUi(mainModule, className, asDialog=False):
    """load ui module related to given mainModule file path

    :param mainModule: package main module file path
    :type mainModule: str
    :param className: name of class to launch
    :type className: str
    :param asDialog: if True, loads the UI as a modal QDialog that blocks interaction with other windows until closed
    :type asDialog: bool

    :return: ui
    :rtype: module
    """
    baseFolder = os.path.split(mainModule)[0]
    uiFile = os.path.join(baseFolder, 'ui.py')

    spec = importlib.util.spec_from_file_location(f'{className}Ui', uiFile)
    uiModule = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(uiModule)


    toLaunch = getattr(uiModule, f'{className}Ui', None)
    if toLaunch is None:
        print(f'not found: {className}Ui')
        return

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)

    try:
        if asDialog:
            uiInstance = toLaunch(parent=None)
            if isinstance(uiInstance, QtWidgets.QDialog):
                uiInstance.setModal(True)
        else:
            uiInstance = toLaunch()
    except Exception as e:
        print(f"Error while instancing: {e}")
        raise

    return uiInstance


def scrollLayout(parentLayout=None):
    """
    Creates a scrollable layout and adds it to the given parent layout.

    :param parentLayout: The layout to which the scroll area will be added.
    :type parentLayout: QtWidgets.QLayout

    :return: The content layout inside the scroll area, where widgets can be added.
    :rtype: QtWidgets.QVBoxLayout
    """
    scrollArea = QtWidgets.QScrollArea()
    scrollArea.setWidgetResizable(True)

    contentWidget = QtWidgets.QWidget()
    contentLayout = QtWidgets.QVBoxLayout(contentWidget)

    scrollArea.setWidget(contentWidget)

    if parentLayout:
        parentLayout.addWidget(scrollArea)

    return scrollArea, contentLayout
