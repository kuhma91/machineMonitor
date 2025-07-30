"""
===============================================================================
fileName: machineMonitor.machineManager.core
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import json

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
BASE_FOLDER = os.sep.join(__file__.split(os.sep)[:-2])
ICON_FOLDER = os.path.join(BASE_FOLDER, 'icon')
NEEDED_INFOS = {'sector': ['1A', '1B', '1C', '2A', '2B', '2C'],
                'usage': ['CNC', 'decoupe laser', 'imprimantes 3D'],
                'manufacturer': None,
                'serial_number': None,
                "year_of_acquisition": None,
                'in_service': True}
MACHINE_FOLDER = os.path.join(BASE_FOLDER, 'data', 'machines')
BUTTONS = ['edit', 'delete', 'add']


def addEntry(name, data):
    """
    Add or update a machine entry by saving data to a JSON file in MACHINE_FOLDER.

    :param name: The machine identifier used as the file name.
    :type name: str
    :param data: The data to store in the machine's JSON file.
    :type data: dict
    """
    if not os.path.exists(MACHINE_FOLDER):
        os.makedirs(MACHINE_FOLDER)
        print(f'created folder : {MACHINE_FOLDER}')

    jsonFile = os.path.join(MACHINE_FOLDER, f'{name}.json')

    with open(jsonFile, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        print(f'add archive : {jsonFile}')


def deleteEntry(name):
    """
    Delete a machine entry by removing its JSON file from MACHINE_FOLDER.

    :param name: The machine identifier whose file will be deleted.
    :type name: str
    """
    jsonFile = os.path.join(MACHINE_FOLDER, f'{name}.json')

    os.remove(jsonFile)
    print(f'deleted archive : {jsonFile}')


def getMachineData(machineName=None):
    """
    Load machine data from JSON files in MACHINE_FOLDER.

    If machineName is provided, only load that machine's data.
    Returns an empty dict if MACHINE_FOLDER does not exist or no matching file is found.

    :param machineName: The specific machine identifier to load data for, or None to load all machines.
    :type machineName: str or None

    :return: A dict mapping machine identifiers to their loaded data.
    :rtype: dict
    """
    if not os.path.exists(MACHINE_FOLDER):
        return {}

    data = {}
    for item in os.listdir(MACHINE_FOLDER):
        if not item.endswith('.json'):
            continue

        shortName = os.path.splitext(item)[0]
        if machineName and shortName != machineName:
            continue

        itemPath = os.path.join(MACHINE_FOLDER, item)
        with open(itemPath, 'r', encoding='utf-8') as f:
            data[shortName] = json.load(f)

    return data
