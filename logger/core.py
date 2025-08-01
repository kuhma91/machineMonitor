"""
===============================================================================
fileName: machineMonitor.logger.core
scripter: angiu
creation date: 22/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import re
import json
from datetime import datetime
from datetime import timedelta

# ==== third ==== #

# ==== local ===== #
from machineMonitor.library.general.infoLib import COLORS
from machineMonitor.library.general.infoLib import getUUID

# ==== global ==== #
BASE_FOLDER = os.sep.join(__file__.split(os.sep)[:-2])
DATA_REPO = os.path.join(BASE_FOLDER, 'data')
LOGS_REPO = os.path.join(DATA_REPO, 'logs')
MACHINE_REPO = os.path.join(DATA_REPO, 'machines')
ICON_FOLDER = os.path.join(BASE_FOLDER, 'icon')
AUTHORISATIONS = {'supervisor': ['edit', 'delete'], 'lead': ['edit']}
LOG_TYPES = ['empty consumable & reload', 'info', 'error']
R, G, B = COLORS['yellow']
NO_MACHINE_CMD = (f"QComboBox {{ border: 2px solid rgb({R}, {G}, {B});"
                  f"color: rgb(212, 212, 212); "
                  f"background-color: rgb(85, 85, 85)}}")
DATE_FILE_PATTERN = re.compile(r'^(?P<year>\d{4})_(?P<month>0[1-9]|1[0-2])_(?P<day>0[1-9]|[12]\d|3[01])$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
EXCLUDED_KEYS = ['file', 'machineData', 'comment', 'timeStamp']


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


def deleteLogs(logUuid):
    """
    Delete the log file corresponding to the given UUID from LOGS_REPO.

    :param logUuid: The UUID of the log to delete.
    :type logUuid: str

    :return: None if the file was deleted or not found, otherwise the caught Exception.
    :rtype: None or Exception
    """
    relatedFile = os.path.join(LOGS_REPO, f'{logUuid}.json')
    if not os.path.exists(relatedFile):
        print(f'not found : {relatedFile}')
        return None

    try:
        os.remove(relatedFile)
        print(f'deleted : {relatedFile}')
        return None

    except Exception as e:
        return e


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


def getDataFromFile(filePath):
    """
    Load data from the given file path, handling JSON and TXT formats.

    :param filePath: Path to the file to read.
    :type filePath: str

    :return: Parsed data as a dict, or an empty dict if the file does not exist or format is unsupported.
    :rtype: dict
    """
    if not filePath or not os.path.exists(filePath):
        return {}

    with open(filePath, 'r', encoding='utf-8') as f:
        if filePath.endswith('.json'):
            return json.load(f)

        if filePath.endswith('.txt'):
            return {l.split('-')[-1].split(':')[0].strip(): l.split(':')[-1].strip() for l in f.readlines()}

        return {}


def getDataFromUuid(logsUuid):
    """
    Load JSON data for the given log UUID.

    :param logsUuid: The UUID of the log file (without extension).
    :type logsUuid: str

    :return: Parsed JSON content as a dict, or an empty dict if the file is missing.
    :rtype: dict
    """
    logsPath = os.path.join(LOGS_REPO, f'{logsUuid}.json')
    if not os.path.exists(logsPath):
        return {}

    with open(logsUuid, 'r', encoding='utf-8') as f:
        return json.load(f)


def getEmployeesData():
    """
    Load employee data from the 'employes.csv' file.

    :return: each employee’s trigram to a dict of their fields, or 'user' if the file is missing.
    :rtype: dict
    """
    data = {}

    employeesFile = os.path.join(DATA_REPO, 'users', 'employs.json')
    if not os.path.exists(employeesFile):
        return data

    with open(employeesFile, 'r', encoding='utf-8') as f:
        data = json.load(f)

        result = {}
        for fullName, info in data.items():
            info['fullName'] = fullName
            trigram = info.pop('trigram')
            result[trigram] = info

    return result


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
        shortName = os.path.splitext(item)[0].split('__')[0]
        if not re.match(DATE_FILE_PATTERN, shortName):
            continue

        data[shortName] = os.path.join(folder, item)

    if not data:
        return {}

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


def saveData(data, mode='save', logUuid=None):
    """
    Save or update log data in LOGS_REPO according to mode and logUuid.

    :param data: The dictionary to serialize and save.
    :type data: dict
    :param mode:
        - 'save'   → create a new JSON log with a generated UUID
        - 'temp'   → create a timestamped JSON under .temp/<username>/
        - 'backup' → create a timestamped TXT under .temp/error/<username>/
        Any other value prints an error and returns None.
    :type mode: str
    :param logUuid: If provided, update the existing JSON log; otherwise generate a new UUID.
    :type logUuid: str or None

    :return: None if successful or mode unknown, otherwise the caught Exception.
    :rtype: None or Exception
    """
    timeStamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    userName = os.getlogin()

    if not logUuid:
        logUuid = getUUID()

        data.update({'timeStamp': timeStamp, 'userName': userName})

        if mode == 'save':
            filePath = os.path.join(LOGS_REPO, f'{logUuid}.json')

        elif mode == 'temp':
            filePath = os.path.join(LOGS_REPO, '.temp', userName, f'{timeStamp}.json')

        elif mode == 'backup':
            filePath = os.path.join(LOGS_REPO, '.temp', 'error', userName, f'{timeStamp}.txt')

        else:
            print(f'unknown mode : {mode}')
            return None

    else:
        existingData = getDataFromUuid(logUuid)
        existingData.update(data)
        existingData.setdefault('modified', []).append([timeStamp, userName])

        filePath = os.path.join(LOGS_REPO, f'{logUuid}.json')

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

            print(f'{mode} as : {filePath}')
            return None

    except Exception as e:
        print(f'error while saving : {e}')
        return e


def getAllData():
    """
    Retrieve and combine data from all valid log files and their associated machine files.

    Iterates over files in LOGS_REPO with filenames matching UUID_PATTERN, loads each file’s JSON content,
    then loads the corresponding machine JSON from MACHINE_REPO using the 'machineName' field.

    :return: A list of dicts, each containing:
             - 'uuid': the file’s UUID
             - 'file': full path to the log file
             - all fields from the log JSON
             - all fields from the machine JSON
    :rtype: list[dict]
    """
    data = []
    for item in os.listdir(LOGS_REPO):
        uuidValue = os.path.splitext(item)[0]
        if not re.match(UUID_PATTERN, uuidValue):
            continue

        filePath = os.path.join(LOGS_REPO, item)
        info = {'uuid': uuidValue, 'file': filePath}
        with open(filePath, 'r', encoding='utf-8') as f:
            info.update(json.load(f))

        info['date'] = info['timeStamp'].split('__')[0]

        machineName = info.get('machineName', None)
        machineFile = os.path.join(MACHINE_REPO, f'{machineName}.json')
        if os.path.exists(machineFile):
            with open(machineFile, 'r', encoding='utf-8') as f:
                info['machineData'] = json.load(f)

        data.append(info)

    return data


def getCompleterData(excluded=None):
    """
    Generate completion data for specified log fields.

    Iterates over all log entries, filters fields by LOG_FILTERS,
    excludes any values in the `excluded` list, and returns unique values.

    :param excluded: List of values to exclude from the results.
    :type excluded: list or None

    :return: Dict mapping each filter key to a list of unique values.
    :rtype: dict
    """
    allData = getAllData()

    completer = {}
    for data in allData:
        for k, v in data.items():
            if isinstance(v, dict):
                for x, y in v.items():
                    if excluded and y in excluded:
                        continue

                    completer.setdefault(x, []).append(y)

                continue

            if k in EXCLUDED_KEYS:
                continue

            if excluded and v in excluded:
                continue

            completer.setdefault(k, []).append(v)

    return {k: list(set(v)) for k, v in completer.items()}


def getTableWidgetData(filters=None):
    """
    Retrieve table data from logs, optionally filtered by specified values.

    :param filters: List of values to filter entries. If None or empty, returns all data.
    :type filters: list or None

    :return: List of data dicts matching provided filters or all data if no filters.
    :rtype: list[dict]
    """
    allData = getAllData()
    if not filters:
        return allData

    data = []
    for info in allData:
        for k, v in info.items():
            if not isinstance(v, dict):
                if v not in filters:
                    continue

                data.append(info)
                continue

            for x, y in v.items():
                if y not in filters:
                    continue

                data.append(info)
                continue

    return data
