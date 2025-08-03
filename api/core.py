"""
===============================================================================
fileName: core.py
scripter: angiu
creation date: 30/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import ast
from datetime import datetime

# ==== third ==== #
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

# ==== local ===== #
from machineMonitor.api.models import Machine
from machineMonitor.api.models import MachineIn
from machineMonitor.api.models import Log
from machineMonitor.api.models import LogIn
from machineMonitor.api.models import Employ
from machineMonitor.api.models import EmployIn
from machineMonitor.library.sqlLib import getPrimaryColumn
from machineMonitor.library.sqlLib import getTableFromDb
from machineMonitor.library.sqlLib import getRowAsDict
from machineMonitor.library.sqlLib import getAllRows
from machineMonitor.library.sqlLib import getAllColumns
from machineMonitor.library.infoLib import getUUID
from machineMonitor.library.infoLib import AUTHORISATIONS

# ==== global ==== #
PACKAGE_REPO = os.sep.join(__file__.split(os.sep)[:-2])
DB_PATH = os.path.join(PACKAGE_REPO, 'data', 'machineMonitor.db')
MATCHING_OUT_TYPES = {'machines': Machine, 'logs': Log, 'employs': Employ}
MATCHING_IN_TYPES = {'machines': MachineIn, 'logs': LogIn, 'employs': EmployIn}
SQL_KEYS = ['limit', 'offset', 'orderBy', 'descending', 'like', 'iLike']
security = HTTPBearer()  # get token from URL Authorization header


def formatSqlModifiers(sqlData):
    """
    Format SQL modifiers such as ORDER BY, LIMIT, and OFFSET based on provided parameters.

    :param sqlData: Dictionary containing optional SQL modifiers (orderBy, descending, limit, offset).
    :type sqlData: dict[str, any]

    :return: SQL modifiers string to append to a SELECT query.
    :rtype: str
    """
    parts = []

    orderBy = sqlData.get('orderBy')
    if orderBy:
        direction = 'DESC' if sqlData.get('descending') else 'ASC'
        parts.append(f'ORDER BY {orderBy} {direction}')

    limit = sqlData.get('limit')
    if limit:
        parts.append(f'LIMIT {int(limit)}')

    offset = sqlData.get('offset')
    if offset:
        parts.append(f'OFFSET {int(offset)}')

    return ' '.join(parts)


def getAllowedNames(data, credentials : HTTPAuthorizationCredentials=Depends(security)):
    """
    Retrieve list of authorized usernames based on credentials and request data.

    :param data: Dictionary possibly containing 'userName' to filter on.
    :type data: dict
    :param credentials: Security credentials containing user token.
    :type credentials: HTTPAuthorizationCredentials

    :return: List of authorized trigram names, or error message if token invalid.
    :rtype: list[str] | str
    """
    token = credentials.credentials
    allUserInfo = getAllUserInfo()
    userInfo = allUserInfo.get(token)
    if not userInfo:
        return "Invalid or missing token"  # unrecognized user

    authorisation = userInfo['authorisation']
    if authorisation == 'operator':
        return [userInfo['trigram']]

    currentUser = userInfo.get('trigram')
    allowedAuthors = ['operator'] if authorisation == 'lead' else ['operator', 'lead']

    allowed = [v['trigram'] for v in allUserInfo.values() if v['authorisation'] in allowedAuthors]
    if currentUser:
        allowed.extend([v['trigram'] for v in allUserInfo.values() if v['trigram'] == currentUser])

    wanted = data.get('userName', None)
    if not wanted:
        return allowed

    wantedUsers = [wanted] if isinstance(wanted, str) else wanted

    return [x for x in wantedUsers if x in allowed]


def getAllUserInfo():
    """
    Load and return all user information indexed by token.

    :return: Dictionary with token as key and user info as value.
    :rtype: dict
    """
    allUsers = getAllRows(DB_PATH, 'employs')
    return {u.get('token'): u for u in allUsers}


def getDataTypesAndColumns(data):
    """
    Filter and organize input data based on database tables and their columns.

    :param data: Dictionary containing input data, including 'dataType' (str or list) and possible table columns.
    :type data: dict

    :return: Dictionary mapping each valid table name to a sub-dictionary of matching column data.
    :rtype: dict
    """
    tables = getTables(data)

    result = {}
    for tableType in tables:
        columns = getAllColumns(DB_PATH, tableType)
        result[tableType] = {k: v for k, v in data.items() if k in columns}

    return result


def getInfo(dataType, filters):
    """
    Retrieve a single log by its UUID.

    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param filters: Primary key of the record to delete.
    :type filters: dict[str, any]

    :return: Log record matching the UUID.
    :rtype: Log
    """

    # check dataType
    primaryColumn = getPrimaryColumn(DB_PATH, dataType)
    if not primaryColumn:
        raise ValueError(f'no primeKey found in: {DB_PATH} -> {dataType}')

    dataTypes = getTableFromDb(DB_PATH)
    if not dataTypes:
        raise ValueError(f'no data types found in: {DB_PATH}')

    if dataType not in dataTypes:
        raise ValueError(f'{dataType} not in: {DB_PATH}')

    # check if enough info given to get result
    rows = getAllRows(DB_PATH, dataType)

    result = []
    for row in rows:
        obj = MATCHING_OUT_TYPES[dataType](**row)  # Instantiate Pydantic model (Machine or Log)
        record = obj.model_dump()  # serialize to dict

        # Apply filters if provided
        if not all(record.get(k) == v for k, v in filters.items()):
            continue

        result.append(record)

    return result


def getRelatedTables(data):
    """
    Identify which tables contain the provided filter keys.

    :param data: Mapping of filter keys to values.
    :type data: dict[str, any]

    :return: A dict mapping each matching table name to its subset of filters.
    :rtype: dict[str, dict[str, any]]
    """
    tables = {}
    for table in getTableFromDb(DB_PATH):
        # Fetch all column names for this table
        columns = getAllColumns(DB_PATH, table)
        # Determine which filters apply to this table
        matching = [col for col in columns if col in data]
        if not matching:
            continue

        # Determine which filters apply to this table
        tables[table] = {k: v for k, v in data.items() if k in columns}

    return tables


def getRequestCmd(dataType, data=None, sqlData=None):
    """
    Build a SQL SELECT command with parameterized WHERE filters.

    :param dataType: Name of the table to query.
    :type dataType: str
    :param data: Mapping of column names to filter values.
    :type data: dict[str, any]
    :param sqlData: Mapping of SQL value to filter values (limit, offset, sortedBy, ect.)
    :type sqlData: dict[str, any]

    :return: A tuple with the SQL command string and the corresponding values.
    :rtype: tuple[str, tuple]
    """
    values = []
    whereParts = []

    if data:
        for k, v in data.items():
            if isinstance(v, str):
                whereParts.append(f'{k} = ?')
                values.append(v)

            elif isinstance(v, bool):
                whereParts.append(f'{k} = ?')
                values.append(1 if v else 0)

            elif isinstance(v, list):
                placeholders = ', '.join(['?'] * len(v))
                whereParts.append(f'{k} IN ({placeholders})')
                values.extend(v)

    cmd = f"SELECT * FROM {dataType}"

    if whereParts:
        cmd += ' WHERE ' + ' AND '.join(whereParts)

    likes = sqlData.get('like', {}) if sqlData else None
    if likes:
        likeParts = [f'{x} ILIKE ?' if sqlData.get('iLike') else f'{x} LIKE ?' for x in likes]
        cmd += ' AND ' + ' AND '.join(likeParts)
        values.extend([f'%{x}%' for x in likes.values()])

    cmd += ' ' + formatSqlModifiers(sqlData)

    return cmd.strip(), tuple(values)


def getTables(data):
    """
    Retrieve a list of table names based on the 'dataType' field in the input data.

    :param data: Dictionary potentially containing a 'dataType' key (str or list-like string).
    :type data: dict

    :return: List of matching table names from the database.
    :rtype: list[str]
    """
    dataType = data.get('dataType')
    allTables = getTableFromDb(DB_PATH)

    if not dataType:
        tables = allTables  # No filter, return all tables

    else:
        try:
            # Try to parse stringified list
            dataTypes = ast.literal_eval(dataType)
            if not isinstance(dataTypes, list):
                dataTypes = [dataTypes]

        except Exception:
            dataTypes = [dataType]  # Fallback if eval fails

        # Filter only matching tables
        tables = [t for t in allTables if t in dataTypes]

    return tables


def getUnSerializedValue(dataType, data, inModel=False):
    """
    Retrieve and deserialize a database record into a Pydantic output model.

    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param data: Mapping containing the primary key field.
    :type data: dict[str, any]

    :return: Pydantic model instance for the requested record.
    :rtype: BaseModel
    """
    # determine primary key column for this table
    primaryKey = getPrimaryColumn(DB_PATH, dataType)
    # fetch raw row as dict
    row = getRowAsDict(DB_PATH, dataType, data[primaryKey])

    # instantiate and return the correct Pydantic model
    cmd = MATCHING_IN_TYPES if inModel else MATCHING_OUT_TYPES

    return cmd[dataType](**row)


def hasAccess(credentials : HTTPAuthorizationCredentials=Depends(security)):
    """
    Check if the user has a valid token and belongs to an authorized role.

    :param credentials: Security credentials containing user token.
    :type credentials: HTTPAuthorizationCredentials

    :return: True if the user has access, False otherwise.
    :rtype: bool
    """
    token = credentials.credentials

    usersInfo = getAllUserInfo()
    userData = usersInfo.get(token)
    if not userData:
        return False

    return userData.get('authorisation') in AUTHORISATIONS


def logInToDict(logIn, dataType):
    """
    Convert a Pydantic input model into a dict and add metadata for logs.

    :param logIn: Pydantic model instance containing input data.
    :type logIn: BaseModel
    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str

    :return: Serialized data dict ready for database insertion.
    :rtype: dict[str, any]
    """
    data = logIn.model_dump()  # extract a dict from given LogIn

    # if inserting into logs, add timestamp, user and uuid
    if dataType == 'logs':
        # Serialize incoming Pydantic model to dict
        data.update({
            'timeStamp': datetime.now().strftime('%Y_%m_%d__%H_%M_%S'),
            'userName': os.getlogin(),
            'uuid': getUUID()
        })

    return data
