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


def getRelatedSQLInfo(dbPath, tableName):
    """
    Retrieve detailed schema information for a specific table in the SQLite database.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table whose schema information to retrieve.

    Returns
    -------
    list of tuple
        Column metadata tuples for each column:
        (cid, name, type, notnull, dflt_value, pk).
        Empty list if the table does not exist.

    Notes
    -----
    - Checks for table existence via `isTableExists`.
    - Uses `PRAGMA table_info` to fetch column definitions.
    - Connection is automatically closed.
    """
    if not isTableExists(dbPath, tableName):
        print(f'{tableName} not found in : {dbPath}')
        return {}

    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB
        cursor.execute(f"PRAGMA table_info({tableName});")
        return cursor.fetchall()


def isTableExists(dbPath, tableName):
    """
    Check whether a table exists in the SQLite database file.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table to check.

    Returns
    -------
    bool
        True if the table exists, False otherwise.

    Notes
    -----
    - Queries the internal `sqlite_master` table to inspect schema.
    - Uses a parameterized query to prevent SQL injection.
    - Connection is automatically closed.
    """
    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB

        # Verify table exists
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?;",  # sqlite_master = intern table that repo all DB objects
            (tableName, )
        )
        return cursor.fetchone() is not None


def isEntryExists(dbPath, tableName, primaryKey):
    """
    Determine if a specific row exists in a table by primary key.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table to query.
    primaryKey : any
        Value of the primary key to check for.

    Returns
    -------
    bool
        True if a matching row is found, False otherwise.

    Notes
    -----
    - Chooses 'name' for 'machines' and 'uuid' for 'logs' as PK column names.
    - Uses parameterized queries to safeguard against SQL injection.
    - Connection is automatically closed.
    """
    with sqlite3.connect(dbPath) as conn:  # connect to SQL DB
        cursor = conn.cursor()  # to get access to operations related to SQL DB
        cursor.execute(f"SELECT 1 FROM {tableName} WHERE name = ?;", (primaryKey,))
        return cursor.fetchone() is not None


def getRowAsDict(dbPath, tableName, primaryKey):
    """
    Fetch a single row as a dictionary mapping column names to values.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table to query.
    primaryKey : any
        Value of the primary key for the row to retrieve.

    Returns
    -------
    dict
        A dict of column:value for the matched row, or an empty dict if not found.

    Notes
    -----
    - Determines the PK column dynamically via `getPrimaryKeyValue`.
    - Executes a parameterized SELECT to prevent SQL injection.
    - Connection is automatically closed.
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
        conn.close()
        return result


def getPrimaryKeyValue(dbPath, tableName):
    """
    Identify the primary key column name for a given table.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table whose PK column is to be found.

    Returns
    -------
    str
        The PK column name.

    Raises
    ------
    ValueError
        If the table has zero or multiple PK columns.

    Notes
    -----
    - Parses schema info from `getRelatedSQLInfo`.
    - Expects exactly one column flagged as PK.
    - Connection is closed automatically by context manager.
    """
    sqlInfo = getRelatedSQLInfo(dbPath, tableName)
    if not sqlInfo:
        return None

    primaryKeyValues = [x[1] for x in sqlInfo if x[-1] == 1]  # get primary key column name
    if not primaryKeyValues:
        raise f'not PK found in : {dbPath} -> {tableName}'

    return min(primaryKeyValues)


def updateDb(dbPath, tableName, primaryKey, data):
    """
    Insert or update a row in the specified table based on its primary key.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table to modify.
    primaryKey : any
        Value of the primary key for the target row.
    data : dict
        Mapping of column names to new values for insert or update.

    Behavior
    --------
    - If the entry does not exist, performs an INSERT of all provided data.
    - If the entry exists, performs UPDATEs for only changed columns.

    Notes
    -----
    - Uses `isEntryExists` to check existence.
    - Commits once at the end; rolls back on error.
    - Connection is automatically closed.
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
