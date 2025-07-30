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
from machineMonitor.library.general.sqlLib import syncDatabase

# ==== global ==== #
PACKAGE_PATH = os.sep.join(__file__.split(os.sep)[:-2])
DB_PATH = os.path.join(PACKAGE_PATH, 'data', 'machineMonitor.db')
REPOS = {
    'machines': os.path.join(PACKAGE_PATH, 'data', 'machines'),
    'logs': os.path.join(PACKAGE_PATH, 'data', 'logs')
}
BOOLEAN_CONVERTER = {True: ['oui', 'o', 'yes', 'y', 'true'], False: ['non', 'n', 'no', 'false']}
MATCHING_TYPES = {'TEXT': str, 'BOOLEAN': bool, 'INTEGER': int}


def publishFromLocal():
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
    data = {}
    for tableName, folder in REPOS.items():
        relatedDBInfo = getRelatedSQLInfo(DB_PATH, tableName)
        if not relatedDBInfo:
            continue

        for filename  in os.listdir(folder):
            if not filename .endswith('.json'):
                continue

            keyName = os.path.splitext(filename)[0]
            path = os.path.join(folder, filename)

            filePath = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                jsonData = json.load(f)

            toSync = {}
            for info in relatedDBInfo:
                columnName, columnType, required, isPrimKey = info[1], info[2], info[3], info[5]
                if isPrimKey:
                    toSync[columnName] = keyName
                    continue

                # check if value missing and if it's a required value
                raw = jsonData.get(columnName)
                if not raw:
                    if not required:
                        continue

                    raise ValueError(f'missing {columnName} in : {filePath}')

                # Conversion from data type
                if columnType == 'BOOLEAN':
                    booleanValue = [k for k, v in BOOLEAN_CONVERTER.items() if raw.lower() in v]
                    if not booleanValue:
                        raise ValueError(f"can't convert : {raw} as boolean")

                    toSync[columnName] = booleanValue[0]

                else:
                    toSync[columnName] = MATCHING_TYPES[columnType](raw)

            data.setdefault(tableName, []).append(toSync)

    syncDatabase(DB_PATH, data)


if __name__ == '__main__':
    publishFromLocal()
