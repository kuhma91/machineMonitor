"""
===============================================================================
fileName: sqlLib
scripter: angiu
creation date: 28/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import sqlite3

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #


def getPrimaryKeyValue(dbPath, tableName):
    """
    Identify the primary key column name for a given table.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table to query.
    :type tableName: str

    :return: The PK column name or If the table has zero or multiple PK columns.
    :rtype: str or ValueError
    """
    sqlInfo = getRelatedSQLInfo(dbPath, tableName)
    if not sqlInfo:
        return None

    primaryKeyValues = [x[1] for x in sqlInfo if x[-1] == 1]  # get primary key column name
    if not primaryKeyValues:
        print(f'not PK found in : {dbPath} -> {tableName}')
        return None

    return min(primaryKeyValues)


def getRelatedSQLInfo(dbPath, tableName):
    """
    Retrieve detailed schema information for a specific table in the SQLite database.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table whose schema information to retrieve.
    :type tableName: str

    :return: Column metadata tuples for each column: (cid, name, type, notnull, dflt_value, pk).
             Empty list if the table does not exist.
    :rtype: list of tuple
    """
    if not isTableExists(dbPath, tableName):
        print(f'{tableName} not found in : {dbPath}')
        return {}

    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB
        cursor.execute(f"PRAGMA table_info({tableName});")
        return cursor.fetchall()


def getRowAsDict(dbPath, tableName, primaryKey):
    """
    Fetch a single row as a dictionary mapping column names to values.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table to query.
    :type tableName: str
    :param primaryKey: Value of the primary key to check for.
    :type primaryKey: any

    :return: A dict of column:value for the matched row, or an empty dict if not found.
    :rtype: dict
    """
    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB

        primaryColumn = getPrimaryKeyValue(dbPath, tableName)
        if not primaryColumn:
            print(f'no primaryColumn found in : {dbPath} -> {tableName}')
            return {}

        cursor.execute(f"SELECT * FROM {tableName} WHERE {primaryColumn} = ?;", (primaryKey,))  # get row which primary key matches given primary key
        row = cursor.fetchone()

        columns = [description[0] for description in cursor.description]  # get columns name

        result = dict(zip(columns, row))  # build dict
        return result


def getTableFromDb(dbPath):
    """
    Return a list of all table names in the SQLite database.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str

    :return: existing table from db
    :rtype: list[str]
    """
    # Open a connection (auto‑closed)
    with sqlite3.connect(dbPath) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")  # Query the internal sqlite_master table for all tables
        return [row[0] for row in cursor.fetchall()]  # Fetch all rows, each row is a tuple (table_name,)


def isEntryExists(dbPath, tableName, primaryKey):
    """
    Determine if a specific row exists in a table by primary key.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table to query.
    :type tableName: str
    :param primaryKey: Value of the primary key to check for.
    :type primaryKey: any

    :return: True if a matching row is found, False otherwise.
    :rtype: bool
    """
    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB
        primaryKeyColumn = getPrimaryKeyValue(dbPath, tableName)  # Dynamically fetch the name of the primary key column
        if not primaryKeyColumn:
            return False

        cursor.execute(f"SELECT 1 FROM {tableName} WHERE {primaryKeyColumn} = ?;", (primaryKey,))
        return cursor.fetchone() is not None


def isTableExists(dbPath, tableName):
    """
    Check whether a table exists in the SQLite database file.

    :param dbPath: Path to the SQLite database file.
    :type dbPath : str
    :param tableName: Name of the table to check.
    :type tableName: str

    :return: True if the table exists, False otherwise.
    :rtype: bool
    """
    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB

        # Verify table exists
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?;",  # sqlite_master = intern table that repo all DB objects
            (tableName, )
        )
        return cursor.fetchone() is not None


def updateDb(dbPath, tableName, primaryKey, data):
    """
    Insert or update a row in the specified table based on its primary key.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table to query.
    :type tableName: str
    :param primaryKey: Value of the primary key to check for.
    :type primaryKey: any
    :param data: Mapping of column names to new values for insert or update.
    :type data: dict
    """
    conn = sqlite3.connect(dbPath)  # connect to SQL DB
    cursor = conn.cursor()  # to get access to operations related to SQL DB

    # INSERT key if does not exists
    if not isEntryExists(dbPath, tableName, primaryKey):
        placeHolders = ', '.join('?' for _ in data)
        columnStr = ', '.join(list(data.keys()))
        sqlCmd = f'INSERT INTO {tableName} ({columnStr}) VALUES ({placeHolders});'
        cursor.execute(sqlCmd, list(data.values()))

    else:
        primaryColumn = getPrimaryKeyValue(dbPath, tableName)
        if not primaryColumn:
            raise f'{primaryKey} even exists in {dbPath} -> {tableName}\n\nbut no primaryKey found in table'

        currentData = getRowAsDict(dbPath, tableName, primaryKey)
        if not currentData:
            raise f'no data found in : {dbPath} -> {tableName} -> {primaryKey}'

        toUpdate = {column: value for column, value in data.items() if currentData[column] != value}
        for columns, value in toUpdate.items():
            sqlCmd = (f"UPDATE {tableName} "  # table to modify
                      f"SET {columns} = ? "  # columns to update
                      f"WHERE {primaryColumn} = ? ")  # term that target the only line to update

            cursor.execute(sqlCmd, (value, primaryKey))
    try:
        print(f'{dbPath} -> {tableName} -> {primaryKey} updated')
        conn.commit()

    except Exception as e:
        print(f'fail to update {dbPath} -> {tableName} -> {primaryKey} : {e}')
        conn.rollback()

    finally:
        conn.close()
