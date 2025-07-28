"""
===============================================================================
fileName: main
scripter: angiu
creation date: 28/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import json

# ==== third ==== #

# ==== local ===== #
from machineMonitor.library.general.sqlLib import getRelatedSQLInfo
from machineMonitor.library.general.sqlLib import updateDb

# ==== global ==== #
PACKAGE_PATH = os.sep.join(__file__.split(os.sep)[:-2])
DB_PATH = os.path.join(PACKAGE_PATH, 'data', 'machineMonitor.db')
REPOS = {
    'machines': os.path.join(PACKAGE_PATH, 'data', 'machines'),
    'logs': os.path.join(PACKAGE_PATH, 'data', 'logs')
}
BOOLEAN_CONVERTER = {True: ['oui', 'o', 'yes', 'y', 'true'], False: ['non', 'n', 'no', 'false']}
MATCHING_TYPES = {'TEXT': str, 'BOOLEAN': bool, 'INTEGER': int}


def syncDB():
    """
    Synchronize local JSON data files into the SQLite database.

    Iterates over each table in REPOS, loads corresponding JSON files,
    converts their fields to the appropriate types, and inserts or updates
    records via `updateDb`.

    Raises
    ------
    ValueError
        If a required field is missing or cannot be converted to the expected type.
    """
    for tableName, folder in REPOS.items():
        relatedDBInfo = getRelatedSQLInfo(DB_PATH, tableName)
        if not relatedDBInfo:
            continue

        for item in os.listdir(folder):
            if not item.endswith('.json'):
                continue

            shortName = os.path.splitext(item)[0]

            filePath = os.path.join(folder, item)
            with open(filePath, 'r', encoding='utf-8') as f:
                jsonData = json.load(f)

                toInsert = {}
                for info in relatedDBInfo:
                    key = info[1]
                    if info[0] == 0 and info[-1] == 1:
                        toInsert[key] = shortName
                        continue

                    value = jsonData.get(info[1])
                    if not value:
                        if info[3] != 1:
                            continue

                        raise ValueError(f'missing {info[1]} in : {filePath}')

                    if isinstance(value, MATCHING_TYPES[info[2]]):
                       toInsert[key] = value
                       continue

                    if info[2] == 'BOOLEAN':
                        boolValue = [k for k, v in BOOLEAN_CONVERTER.items() if value.lower() in v]
                        if not boolValue:
                            raise ValueError(f"can't convert : {value} as boolean")

                        toInsert[key] = min(boolValue)
                        continue

                    finalValue = MATCHING_TYPES[info[2]](value)
                    toInsert[key] = finalValue

                updateDb(DB_PATH, tableName, shortName, toInsert)
