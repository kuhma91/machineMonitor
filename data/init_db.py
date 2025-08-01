#!/usr/bin/env python3
"""
init_db.py

Initialize a local SQLite database for MachineMonitor.
Creates the tables `machines` and `logs` if they don’t exist.
"""

import sqlite3
import os
import json

from machineMonitor.library.general.sqlLib import getRelatedSQLInfo
from machineMonitor.library.general.sqlLib import syncDatabase


# 1. db based on this module path
DATA_PATH = os.path.split(__file__)[0]
DB_PATH = os.path.join(DATA_PATH, "machineMonitor.db")
REPOS = {
    'machines': os.path.join(DATA_PATH, 'data', 'machines'),
    'logs': os.path.join(DATA_PATH, 'data', 'logs'),
    'employs': os.path.join(DATA_PATH, 'data', 'employs')
}
BOOLEAN_CONVERTER = {True: ['oui', 'o', 'yes', 'y', 'true'], False: ['non', 'n', 'no', 'false']}
MATCHING_TYPES = {'TEXT': str, 'BOOLEAN': bool, 'INTEGER': int}


# DLL : Data Definition Language
DLL = '''
CREATE TABLE IF NOT EXISTS machines (
    name TEXT PRIMARY KEY,
    comment TEXT,
    in_service BOOLEAN NOT NULL,
    manufacturer TEXT NOT NULL,
    sector TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    usage TEXT NOT NULL,
    year_of_acquisition INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS logs(
    uuid TEXT PRIMARY KEY,
    comment TEXT,
    machineName TEXT NOT NULL,
    project TEXT NOT NULL,
    timeStamp TEXT NOT NULL,
    type TEXT NOT NULL,
    userName TEXT NOT NULL,
    modifications TEXT,
    FOREIGN KEY(machineName) REFERENCES machines(name),
    FOREIGN KEY(userName) REFERENCES employs(trigram)
);


CREATE TABLE IF NOT EXISTS employs(
    trigram TEXT PRIMARY KEY,
    token TEXT,
    first_name TEXT,
    last_name TEXT,
    authorisation TEXT
);
'''


def publishFromLocal():
    """
    Synchronize local JSON data files into the SQLite database.

    Iterates over each table in REPOS, loads corresponding JSON files,
    converts their fields to the appropriate types, and inserts or updates
    records via `updateDb`.
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

                # check if value was given and if it's a required value
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


def main():
    conn = sqlite3.connect(DB_PATH)  # open or create dataBase
    try:
        conn.executescript(DLL)  # exec DLL
        conn.commit()  # valid changes
        print(f"[OK] Database initialized at {DB_PATH}")

        publishFromLocal()

    except sqlite3.Error as e:
        print(f"[ERROR] Failed to initialize database: {e}")

    finally:
        conn.close()  # end connection


if __name__ == "__main__":
    main()
