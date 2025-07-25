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
import re
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
DATE_FILE_PATTERN = r'^(?P<year>\d{4})_(?P<month>0[1-9]|1[0-2])_(?P<day>0[1-9]|[12]\d|3[01])\.(?:json|txt)$'



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


def getFileData(folder):
    """
    Retrieve the most recent file in the specified folder matching the date pattern.

    :param folder: Path to the directory containing dated files.
    :type folder: str

    :return: Full path of the latest matching file, or None if folder doesn't exist or no matching files are found.
    :rtype: str or None
    """
    if not os.path.exists(folder):
        return None

    data = {}
    for item in os.listdir(folder):
        if not re.match(DATE_FILE_PATTERN, item):
            continue

        shortName = os.path.splitext(item)[0].split('__')[0]
        data[shortName] = os.path.join(folder, item)

    if not data:
        return None

    latestDateStr = max(data.keys(), key=lambda ds: datetime.strptime(ds, '%Y_%m_%d'))
    return data[latestDateStr]



def getInitInfo():
    """
    Retrieve the most recent initialization file for the current user and load its contents.

    :return: A tuple (filePath, data, fromError):
        - filePath (str or None): Path to the latest file, or None if none found.
        - data (dict): Parsed contents of the file.
        - fromError (bool): True if the file came from the error folder, False otherwise.
    :rtype: tuple[str or None, dict, bool]
    """
    userName = os.getlogin()
    filePath = getFileData(os.path.join(LOGS_REPO, '.temp', 'error', userName))
    fromError = True
    if not filePath:
        filePath = getFileData(os.path.join(LOGS_REPO, '.temp', userName))
        fromError = False

    return filePath, getDataFromFile(filePath), fromError


def getDataFromFile(filePath):
    """
    Load data from the given file path, handling JSON and TXT formats.

    :param filePath: Path to the file to read.
    :type filePath: str

    :return: Parsed data as a dict, or an empty dict if the file does not exist or format is unsupported.
    :rtype: dict
    """
    if not os.path.exists(filePath):
        return {}

    with open(filePath, 'r', encoding='utf-8') as f:
        if filePath.endswith('.json'):
            return json.load(f)

        if filePath.endswith('.txt'):
            return {l.split('-')[-1].split(':')[0].strip(): l.split(':')[-1].strip() for l in f.readlines()}

        return {}


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


def saveData(data, mode='save'):
    """
    Save data to a file in LOGS_REPO according to the given mode.

    :param data: The dictionary to serialize and save.
    :type data: dict
    :param mode:
        - 'save'   → write a new UUID-named JSON in LOGS_REPO
        - 'temp'   → write a timestamped JSON under .temp/<username>/
        - 'backup' → write a timestamped TXT under .temp/error/<username>/
        Any other value prints an error and does nothing.
    :type mode: str
    :return: None if successful or mode unknown, otherwise returns the caught Exception.
    :rtype: None or Exception
    """
    timeStamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    userName = os.getlogin()
    newUuid = getUUID()

    data.update({'timeStamp': timeStamp, 'userName': userName})

    if mode == 'save':
        filePath = os.path.join(LOGS_REPO, f'{newUuid}.json')

    elif mode == 'temp':
        filePath = os.path.join(LOGS_REPO, '.temp', userName, f'{timeStamp}.json')

    elif mode == 'backup':
        filePath = os.path.join(LOGS_REPO, '.temp', 'error', userName, f'{timeStamp}.txt')

    else:
        print(f'unknown mode : {mode}')
        return

    folder = os.path.split(filePath)[0]
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f'created : {folder}')

    try:
        with open(filePath, 'w', encoding='utf-8') as f:
            if filePath.endswith('.json'):
                json.dump(data, f)

            elif filePath.endswith('.txt'):
                f.write('\n'.join([f'- {k} : {v}' for k, v in data.items()]))

            print(f'backup as : {filePath}')
            return None

    except Exception as e:
        print(f'error while saving : {e}')
        return e