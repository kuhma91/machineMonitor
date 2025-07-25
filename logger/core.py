"""
===============================================================================
fileName: machineMonitor.logger.core
scripter: angiu
creation date: 22/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import uuid
import os
import csv
import json
from datetime import datetime
from datetime import timedelta

# ==== third ==== #

# ==== local ===== #
from machineMonitor.library.general.infoLib import COLORS

# ==== global ==== #
BASE_FOLDER = os.sep.join(__file__.split(os.sep)[:-2])
DATA_REPO = os.path.join(BASE_FOLDER, 'data')
LOGS_REPO = os.path.join(DATA_REPO, 'logs')
ICON_FOLDER = os.path.join(BASE_FOLDER, 'icon')
AUTHORISATIONS = {'supervisor': ['edit', 'delete'], 'lead': ['edit']}
LOG_TYPES = ['empty consumable & reload', 'info', 'error']
R, G, B = COLORS['yellow']
NO_MACHINE_CMD = (f"QComboBox {{ border: 2px solid rgb({R}, {G}, {B});"
                  f"color: rgb(212, 212, 212); "
                  f"background-color: rgb(85, 85, 85)}}")


def getEmployeesData():
    """
    Load employee data from the 'employes.csv' file.

    :return: each employee’s trigram to a dict of their fields, or 'user' if the file is missing.
    :rtype: dict
    """
    data = {}

    employeesFile = os.path.join(DATA_REPO, 'employes.csv')
    if not os.path.exists(employeesFile):
        return data

    titles = None
    with open(employeesFile, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for i, row in enumerate(reader):
            if i == 0:
                titles = [x.strip().lower() for x in row]
                continue

            trigramIndex = [x.strip() for x in titles].index('trigram')
            trigram = row[trigramIndex].strip().lower()
            data[trigram] = {x: row[i].strip().lower() for i, x in enumerate(titles)}

    return data


def getAuthorisation():
    """
    Retrieve the authorization level for the current OS user.

    :return: The authorization level from employees data, or 'user' if the user is not found.
    :rtype: str
    """
    user = os.getlogin().lower()
    employeesData = getEmployeesData()

    if user not in employeesData:
        return 'user'

    return employeesData.get(user, {}).get('authorisation', 'user')


def clearTempData():
    """
    Remove temporary data files older than 3 days from the temp folder.

    This function checks all files returned by getTempData() and deletes
    those whose date (parsed from filename) is more than 3 days before now.
    """
    tempData = getTempData()
    cutoff = datetime.now() - timedelta(days=3)
    for dateStr, filePath in tempData.items():
        fileDate = datetime.strptime(dateStr, '%Y_%m_%d')
        if fileDate < cutoff:
            os.remove(filePath)
            print('deleted: filePath')


def getTempData():
    """
    Collect temporary data files from the user's temp directory.

    Scans LOGS_REPO/.temp/<username>/ for JSON files and returns
    a dict mapping each file's date string (YYYY_MM_DD) to its full path.

    :return: Mapping of date strings to file paths.
    :rtype: dict
    """
    tempFolder = os.path.join(LOGS_REPO, '.temp', os.getlogin())

    tempData = {}
    if not os.path.exists(tempFolder):
        return tempData

    for item in os.listdir(tempFolder):
        relatedDate = os.path.splitext(item)[0].split('__')[0]
        tempData[relatedDate] = os.path.join(tempFolder, item)

    return tempData


def getUUID():
    """
    Generate a new UUID string and ensure it does not collide with existing files in LOGS_REPO.

    :return: A unique UUID as a string.
    :rtype: str
    """
    newId = str(uuid.uuid4())
    if not os.path.exists(LOGS_REPO):
        return newId

    uuids = {os.path.splitext(x)[0] for x in os.listdir(LOGS_REPO)}
    while newId in uuids:
        newId = str(uuid.uuid4())

    return newId


def saveData(data, temp=False):
    """
    Save data to a JSON file in LOGS_REPO, using a timestamped or UUID-based filename.

    :param data: The data to save as JSON.
    :type data: dict
    :param temp: If True, saves under LOGS_REPO/.temp/<username>/ with timestamp; otherwise uses UUID filename.
    :type temp: bool
    """
    timeStamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    userName = os.getlogin()
    newUuid = getUUID()

    if temp:
        fileName = os.path.join(LOGS_REPO, '.temp', userName, f'{timeStamp}.json')
    else:
        fileName = os.path.join(LOGS_REPO, f'{newUuid}.json')

    folder = os.path.split(fileName)[0]
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f'created : {folder}')

    data.update({'timeStamp': timeStamp, 'userName': userName})

    with open(fileName, 'w', encoding='utf-8') as f:
        json.dump(data, f)