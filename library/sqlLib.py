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

def execMultiRequests(dbPath, cmds):
    """
    Execute multiple parameterized SQL commands and collect their results.

    :param dbPath: Filesystem path to the SQLite database file.
    :type dbPath: str
    :param cmds: Mapping of table names to SQL command strings.
    :type cmds: dict[str, tuple[str, tuple]]

    :return: List of row dictionaries with an added 'dataType' field.
    :rtype: list[dict]
    """
    result = []
    with sqlite3.connect(dbPath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for dType, (sql, values) in cmds.items():
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            for row in rows:
                info = dict(row)
                info['dataType'] = dType
                result.append(info)

    return result


def getAllColumns(dbPath, tableName):
    """
    Return the list of column names for a given table in a SQLite database.

    :param dbPath: path to the SQLite file
    :type dbPath: str
    :param tableName: name of the table to inspect
    :type tableName: str

    :return: list of column names in order
    :rtype: list[str]
    """
    if not isTableExists(dbPath, tableName):
        print(f'{tableName} not found in: {dbPath}')
        return []

    with sqlite3.connect(dbPath) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tableName});")
        # cursor.fetchall() => list of tuples (cid, name, type, notnull, dflt_value, pk)
        return [col[1] for col in cursor.fetchall()]


def getAllRows(dbPath, tableName):
    """
    Retrieve all rows from the specified table.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str

    :param tableName: Name of the table to query.
    :type tableName: str

    :return: List of rows as dictionaries mapping column names to values.
    :rtype: list[dict]
    """
    if not isTableExists(dbPath, tableName):
        print(f'{tableName} not found in: {dbPath}')
        return []

    # Open a connection to the database and ensure it’s closed automatically
    with sqlite3.connect(dbPath) as conn:
        # Make each row behave like a dict: column_name → value
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Execute the query to get every row
        cursor.execute(f"SELECT * FROM {tableName};")
        rows = cursor.fetchall()

    # Convert each sqlite3.Row to a plain dict
    return [dict(row) for row in rows]


def getPrimaryColumn (dbPath, tableName):
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
        print(f'{tableName} not found in: {dbPath}')
        return None

    primaryKeyValues = [x[1] for x in sqlInfo if x[-1] == 1]  # get primary key column name
    if not primaryKeyValues:
        print(f'not PK found in: {dbPath} -> {tableName}')
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
        print(f'{tableName} not found in: {dbPath}')
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

        primaryColumn = getPrimaryColumn(dbPath, tableName)
        if not primaryColumn:
            print(f'no primaryColumn found in: {dbPath} -> {tableName}')
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
        primaryKeyColumn = getPrimaryColumn(dbPath, tableName)  # Dynamically fetch the name of the primary key column
        if not primaryKeyColumn:
            return False

        cursor.execute(f"SELECT 1 FROM {tableName} WHERE {primaryKeyColumn} = ?;", (primaryKey,))
        return cursor.fetchone() is not None


def isTableExists(dbPath, tableName):
    """
    Check whether a table exists in the SQLite database file.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
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
            (tableName)
        )
        return cursor.fetchone() is not None


def deleteLine(dbPath, tableName, primKey):
    """
    Delete a single row from the specified table by primary key.

    :param dbPath: Filesystem path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table from which to delete.
    :type tableName: str
    :param primKey: Value of the primary key for the row to delete.
    :type primKey: str
    """
    if not isTableExists(dbPath, tableName):
        raise ValueError(f"'{tableName}' does not exist in database: {dbPath}")

    primColumn = getPrimaryColumn(dbPath, tableName)
    if not primColumn:
        raise ValueError(f"No primary key column found for table '{tableName}' in: {dbPath}")

    existingKeys = {row[primColumn] for row in getAllRows(dbPath, tableName)}
    if primKey not in existingKeys:
        raise ValueError(f"Primary key '{primKey}' not found in table '{tableName}'")

    # Open a connection and commit on success / rollback on error
    conn = sqlite3.connect(dbPath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {tableName} WHERE {primColumn} = ?;", (primKey,))
        conn.commit()
        print(f'deleted: {primKey}')

    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to delete row '{primKey}' from '{tableName}': {e}") from e

    finally:
        conn.close()


def createLine(dbPath, tableName, data):
    """
    Insert a new row into the specified table in the SQLite database.

    :param dbPath: Filesystem path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table to insert into.
    :type tableName: str
    :param data: Dictionary mapping column names to values for the new row.
    :type data: dict[str, any]
    """
    # Check that the table exists
    if not isTableExists(dbPath, tableName):
        raise ValueError(f"'{tableName}' does not exist in database: {dbPath}")

    # Determine the primary key column for this table
    primaryColumn = getPrimaryColumn(dbPath, tableName)
    if not primaryColumn:
        raise ValueError(f"No primary key column found for table '{tableName}' in: {dbPath}")

    # Load existing rows to prevent duplicate primary keys
    existingRows = getAllRows(dbPath, tableName)
    existingPrimaryKeys = {r[primaryColumn]: r for r in existingRows}
    primaryKey = data[primaryColumn]
    if primaryKey in existingPrimaryKeys:
        raise ValueError(f"{primaryKey} even exists in: {dbPath} -> {tableName}")

    # Build the INSERT statement
    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    values = tuple(data.values())

    conn = sqlite3.connect(dbPath)  # connect to the databas
    cursor = conn.cursor()  # to get access to operations related to SQL DB
    try:
        # Execute the insertion and commit
        cursor.execute(f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders});", values)
        conn.commit()
        print(f"added: {primaryKey}")

    except Exception as e:
        # Roll back on error
        conn.rollback()
        raise ValueError(f"Failed to add {primaryKey} in: {tableName} -> {e}") from e

    finally:
        conn.close()


def updateLine(dbPath, tableName, data):
    """
    Update specified columns of a row identified by its primary key in a SQLite table.

    :param dbPath: Filesystem path to the SQLite database file.
    :type dbPath: str
    :param tableName: Name of the table where the row resides.
    :type tableName: str
    :param data: Dictionary containing the primary key and new column values.
    :type data: dict[str, any]
    """
    if not isTableExists(dbPath, tableName):
        raise ValueError(f"'{tableName}' does not exist in database: {dbPath}")

    primaryColumn = getPrimaryColumn(dbPath, tableName)
    if not primaryColumn:
        raise ValueError(f"No primary key column found for table '{tableName}' in: {dbPath}")

    rows = getAllRows(dbPath, tableName)
    primaryValue  = data[primaryColumn]
    existing = [row for row in rows if row[primaryColumn] == primaryValue ]
    if len(existing) >= 1:
        raise ValueError(f"Primary key '{primaryValue }' not found in table '{tableName}'")

    current = existing[0]

    # Open a connection and automatically commit on success / rollback on error
    conn = sqlite3.connect(dbPath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        # Only update columns whose value has changed (skip primary key)
        for column, value in data.items():
            if column == primaryColumn or current[column] == value:
                continue

            cursor.execute(f"UPDATE {tableName} SET {column} = ? WHERE {primaryColumn} = ?;", (value, primaryValue))

        conn.commit()
        print(f"Updated row '{primaryValue}' in '{tableName}' successfully.")

    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to update row '{primaryValue}' from '{tableName}': {e}") from e

    finally:
        conn.close()


def syncDatabase(dbPath, data):
    """
    Synchronize in-memory records with the SQLite database.

    :param dbPath: Path to the SQLite database file.
    :type dbPath: str
    :param data: Mapping tableName -> list of row-dicts.
    :type data: dict[str, list[dict]]
    """
    conn = sqlite3.connect(dbPath)  # connect to SQL DB
    cursor = conn.cursor()  # to get access to operations related to SQL DB

    try:
        for tableName, records in data.items():
            # Determine primary key column
            primaryColumn  = getPrimaryColumn(dbPath, tableName)

            # Load existing rows from DB
            existingRows = getAllRows(dbPath, tableName)
            existingKeys = {row[primaryColumn ] for row in existingRows}

            # Desired keys from input
            desiredKeys = {rec[primaryColumn] for rec in records}

            # DELETE rows not in desiredKeys
            for keyToDelete in existingKeys - desiredKeys:
                # delete obsolete row
                cursor.execute(f"DELETE FROM {tableName} WHERE {primaryColumn} = ?;", (keyToDelete,))
                print(f'deleted: {keyToDelete}')

            # Build a map for fast lookups
            existingMap = {r[primaryColumn]: r for r in existingRows}

            # INSERT new rows or UPDATE existing ones
            for rec in records:
                key = rec[primaryColumn]
                if key not in existingKeys:
                    # insert new row
                    columns = ", ".join(rec.keys())
                    placeholders = ", ".join("?" for _ in rec)
                    values = tuple(rec.values())
                    cursor.execute(f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders});", values)
                    print(f"added: {key}")
                    continue

                # English comment: update changed columns only
                current = existingMap[key]
                for column, value in rec.items():
                    if current[column] == value:
                        continue

                    cursor.execute(f"UPDATE {tableName} SET {column} = ? WHERE {primaryColumn} = ?;", (value, key))
                    print(f"updated: {tableName}.{column} for {key}")

        conn.commit()
        print("Database synchronized successfully.")

    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to synchronize DB: {e}") from e

    finally:
        conn.close()
