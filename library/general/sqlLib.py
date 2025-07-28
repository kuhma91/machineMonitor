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
        Filesystem path to the SQLite database file.
    tableName : str
        Name of the table whose schema information to retrieve.

    Returns
    -------
    list of tuple or None
        If the table exists:
            Returns a list of column metadata tuples:
            (cid, name, type, notnull, dflt_value, pk)
        If the table does not exist:
            Prints a warning and returns None.

    Notes
    -----
    - Verifies table existence by calling `isTableExists` first.
    - Uses `PRAGMA table_info` to fetch column definitions.
    - Closes the database connection after querying.
    """
    if not isTableExists(dbPath, tableName):
        print(f'{tableName} not found in : {dbPath}')
        return None

    conn = sqlite3.connect(dbPath)  # connect to SQL DB
    cursor = conn.cursor()  # to get access to operations related to SQL DB
    cursor.execute(f"PRAGMA table_info({tableName});")
    return cursor.fetchall()


def isTableExists(dbPath, tableName):
    """
    Check if a table with the specified name exists in the given SQLite database file.

    Parameters
    ----------
    dbPath : str
        Filesystem path to the SQLite database file.
    tableName : str
        Name of the table to check for existence.

    Returns
    -------
    bool
        True if the table exists in the database, False otherwise.

    Notes
    -----
    - Opens a new connection for each check to avoid side effects.
    - Uses the internal `sqlite_master` table to query the database schema.
    - Employs parameterized queries to prevent SQL injection.
    """
    conn = sqlite3.connect(dbPath)  # connect to SQL DB
    cursor = conn.cursor()  # to get access to operations related to SQL DB

    # Verify table exists
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?;",  # sqlite_master = intern table that repo all DB objects
        (tableName, )
    )
    return cursor.fetchone() is not None


def isEntryExists(dbPath, tableName, primaryKey):
    """
    Check if an entry with the specified primary key exists in the given table.

    Parameters
    ----------
    dbPath : str
        Filesystem path to the SQLite database file.
    tableType : str
        Name of the table to query (e.g., 'machines' or 'logs').
    primaryKey : str
        Value of the primary key to look up in the table.

    Returns
    -------
    bool
        True if a matching row is found, False otherwise.

    Notes
    -----
    - Opens a new connection for each check to avoid persistent cursors.
    - Uses parameterized queries to safeguard against SQL injection.
    - Assumes the primary key column is named 'name' for 'machines'
      and 'uuid' for 'logs'; adapt as needed for other tables.
    """
    conn = sqlite3.connect(dbPath)  # connect to SQL DB
    cursor = conn.cursor()  # to get access to operations related to SQL DB
    cursor.execute(f"SELECT 1 FROM {tableName} WHERE name = ?;", (primaryKey,))
    return cursor.fetchone() is not None


def getRowAsDict(dbPath, tableName, primaryKey):
    """
    Retrieve a single row from the specified table as a dictionary.

    Parameters
    ----------
    dbPath : str
        Filesystem path to the SQLite database file.
    tableName : str
        Name of the table to query from.
    primaryKey : any
        Value of the primary key for the row to retrieve.

    Returns
    -------
    dict
        A dictionary mapping column names to their corresponding values
        for the matched row. Returns an empty dict if no matching row is found.

    Notes
    -----
    - Uses `getPrimaryKeyValue` to determine the primary key column name dynamically.
    - Executes a parameterized query to avoid SQL injection.
    - Closes the database connection after retrieval.
    """
    conn = sqlite3.connect(dbPath)  # connect to SQL DB
    cursor = conn.cursor()  # to get access to operations related to SQL DB

    primaryColumn = getPrimaryKeyValue(dbPath,tableName)
    cursor.execute(f"SELECT * FROM {tableName} WHERE {primaryColumn} = ?;", (primaryKey,))  # get row which primary key matches given primary key
    row = cursor.fetchone()

    columns = [description[0] for description in cursor.description]  # get columns name

    result = dict(zip(columns, row))  # build dict
    conn.close()
    return result


def getPrimaryKeyValue(dbPath, tableName):
    """
    Identify the name of the primary key column for the given table.

    Parameters
    ----------
    dbPath : str
        Filesystem path to the SQLite database file.
    tableName : str
        Name of the table whose primary key column is to be determined.

    Returns
    -------
    str or None
        The column name that is designated as the primary key, or None if not found.

    Notes
    -----
    - Uses `getRelatedSQLInfo` to fetch schema info and filter the column with pk flag.
    - Assumes exactly one primary key column exists per table.
    - Closes the database connection used for schema inspection.
    """
    sqlInfo = getRelatedSQLInfo(dbPath, tableName)
    return min([x[1] for x in sqlInfo if x[-1] == 1])  # get primary key column name


def updateDb(dbPath, tableName, primaryKey, data):
    """
    Insert or update a row in the given table based on whether the primary key exists.

    Parameters
    ----------
    dbPath : str
        Path to the SQLite database file.
    tableName : str
        Name of the table to modify.
    primaryKey : str
        Value of the table’s primary‑key column for this record.
    data : dict
        Mapping column_name → new_value for all fields you wish to insert or update.

    Behavior
    --------
    1. Si l’entrée n’existe pas (selon `isEntryExists`), on fait un INSERT :
       - On compile la liste des colonnes et des placeholders `?` automatiquement.
    2. Sinon, on :
       a. Récupère les valeurs actuelles (`get_row_as_dict` ou ton `getValues`).
       b. Calcule `toUpdate` : les paires (col, val) où `data[col] != current[col]`.
       c. Pour chaque colonne à mettre à jour, on exécute un UPDATE ciblé.

    Notes
    -----
    - Chaque UPDATE utilise un SQL de la forme
      `UPDATE tableName SET col = ? WHERE pk_col = ?;`
    - On commit après chaque modification pour que ce soit immédiatement persistant.
    - Pense à fermer la connexion à la fin.
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
        currentData = getRowAsDict(dbPath, tableName, primaryKey)
        toUpdate = {column: value for column, value in data.items() if currentData[column] != value}
        for columns, value in toUpdate.items():
            sqlCmd = (f"UPDATE {tableName}"  # table to modify
                      f"SET {columns} = ?"  # columns to update
                      f"WHERE {primaryColumn} = ?")  # term that target the only line to update

            cursor.execute(sqlCmd, (value, primaryKey))
            conn.commit()

    conn.close()
