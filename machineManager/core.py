"""
===============================================================================
fileName: machineMonitor.machineManager.core
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
import json
# ==== native ==== #
import os

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
BASE_FOLDER = os.sep.join(__file__.split(os.sep)[:-2])
ICON_FOLDER = os.path.join(BASE_FOLDER, 'icon')
NEEDED_INFOS = {'secteur': ['1A', '1B', '1C', '2A', '2B', '2C'],
                'type': ['CNC', 'decoupe laser', 'imprimantes 3D'],
                'constructeur': None,
                'numero de serie': None,
                "annee d'acquisition": None,
                'en service': True}
MACHINE_JSON = os.path.join(BASE_FOLDER, 'data', 'machine.json')
BUTTONS = ['edit', 'sub', 'add']


def addEntry(name, data):
    """
    Add or update an entry in the MACHINE_JSON file and save the updated data.

    :param name: The key under which to store the data.
    :type name: str
    :param data: The data to associate with the given key.
    :type data: dict
    """
    if not os.path.exists(MACHINE_JSON):
        currentData = {name: data}

    else:
        currentData = getMachineData()
        currentData[name] = data

    saveData(currentData)


def deleteEntry(name):
    """
    Delete the specified entry from the MACHINE_JSON file and save the updated data.

    :param name: The key of the entry to delete.
    :type name: str
    """
    if not os.path.exists(MACHINE_JSON):
        return

    currentData = getMachineData()
    currentData.pop(name, None)

    saveData(currentData)


def getMachineData():
    """
    Load machine data from the MACHINE_JSON file.
    Checks if MACHINE_JSON exists; returns an empty dict if not.

    :return: Parsed machine data as a dict, or empty dict if file is missing.
    :rtype: dict
    """
    if not os.path.exists(MACHINE_JSON):
        return {}

    return json.load(open(MACHINE_JSON, 'r', encoding='utf-8'))


def saveData(data):
    """
    Save the given data to the MACHINE_JSON file in JSON format.

    :param data: The data to write to the JSON file.
    :type data: dict
    """
    with open(MACHINE_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    print(f'saved as : {MACHINE_JSON}')
