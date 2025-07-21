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
BUTTONS = ['add', 'sub', 'edit']


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


def saveData(name, data):
    """
    Save the provided data under the given name in the MACHINE_JSON file.

    :param name: Key under which the data will be stored.
    :type name: str
    :param data: Data to save; must be JSON‑serializable.
    :type data: Any
    """
    if not os.path.exists(MACHINE_JSON):
        currentData = {name: data}

    else:
        currentData = getMachineData()
        currentData[name] = data

    with open(MACHINE_JSON, 'w', encoding='utf-8') as f:
        json.dump(currentData, f)

    print('saved as : {}')