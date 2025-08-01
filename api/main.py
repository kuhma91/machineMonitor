"""
===============================================================================
fileName: main.py
scripter: angiu
creation date: 29/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import json

# ==== third ==== #
from fastapi import FastAPI
from fastapi import status
from fastapi import Request
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

# ==== local ===== #
from machineMonitor.library.general.sqlLib import getPrimaryColumn
from machineMonitor.library.general.sqlLib import getTableFromDb
from machineMonitor.library.general.sqlLib import getAllRows
from machineMonitor.library.general.sqlLib import isTableExists
from machineMonitor.library.general.sqlLib import updateLine
from machineMonitor.library.general.sqlLib import createLine
from machineMonitor.library.general.sqlLib import deleteLine
from machineMonitor.library.general.sqlLib import execMultiRequests
from machineMonitor.api.core import getUnSerializedValue, hasAccess
from machineMonitor.api.core import getAllowedNames
from machineMonitor.api.core import logInToDict
from machineMonitor.api.core import getRelatedTables
from machineMonitor.api.core import getRequestCmd
from machineMonitor.api.core import DB_PATH

# ==== global ==== #
print(f"Loading FastAPI app from: {__file__}")

app = FastAPI()  # lowerCase -> conventional
security = HTTPBearer()  # get token from URL Authorization header


@app.post("/{dataType}", status_code=status.HTTP_204_NO_CONTENT,  summary="add line from given type and data")
def createRecord(dataType, data):
    """
    add a record from the specified table.

    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param data: provided by the user to create a machine.
    :type data: LogIn
    """
    # convert Login as dict
    recordDict = logInToDict(data, dataType)

    # Insert into database
    createLine(DB_PATH, dataType, recordDict)

    # get new created row
    return getUnSerializedValue(dataType, recordDict, True)


@app.delete("/{dataType}/{pk}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item from given type and primaryKey")
def deleteRecord(dataType, pk):
    """
    Delete a record from the specified table.

    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param pk: Primary key of the record to delete.
    :type pk: str
    """
    try:
        deleteLine(DB_PATH, dataType, pk)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/{dataType}", response_model=list[dict], summary="search from filters")
def dynamicRequest(credentials=Depends(security), dataType=None, request=None, limit=None, offset=None, orderBy=None, descending=False, like=None, iLike=None):
    """
    Retrieve machines with optional filters from query string.

    :param credentials: Token credentials extracted from the HTTP Authorization header.
    :type credentials: fastapi.security.HTTPAuthorizationCredentials
    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param request: FastAPI request object containing query_params.
    :type request: Request
    :param limit: max items number to return
    :type limit: int
    :param offset: items number to ignore before start to return
    :type offset: int
    :param orderBy: column name to sort result by
    :type orderBy: str
    :param descending: sorted or reversed
    :type descending: bool
    :param like: concerned column and related text that related cells have to contain
    :type like: Request
    :param iLike: is given like sensible to case (upper or lower)
    :type iLike: bool

    :return: List of Machine instances matching filters.
    :rtype: list[dict]
    """
    sqlData = {
        'limit': limit, 'offset': offset, 'orderBy': orderBy, 'descending': descending, 'like': like, 'iLike': iLike
    }

    if not hasAccess(credentials):
        raise HTTPException(status_code=401, detail="Invalid or missing token")  # unrecognized user

    data = dict(request.query_params)

    cmds = {}
    # If a specific table is requested
    if dataType:
        # ensure the table exists
        if not isTableExists(DB_PATH, dataType):
            raise ValueError(f'{dataType} does not exist in : {DB_PATH}')

        if dataType == 'logs':
            data['userName'] = getAllowedNames(credentials, data)

        # no filters provided: return full table
        if not request:
            return getAllRows(DB_PATH, dataType)

        cmds[dataType] = getRequestCmd(dataType, data, sqlData)

    else:
        # No specific table, but no filters: return all rows from all tables
        if not request:
            result = []
            for table in getTableFromDb(DB_PATH):
                for rowDict in getAllRows(DB_PATH, table):
                    # annotate row with its source table
                    rowDict['dataType'] = table
                    result.append(rowDict)

            return result

        # Determine which tables the filter keys belong to
        tables = getRelatedTables(dict(request.query_params))
        for table, relatedFilters in tables.items():
            if table == 'logs':
                relatedFilters['userName'] = getAllowedNames(credentials, data)

            # build a SELECT command per matching table
            cmds[table] = getRequestCmd(table, relatedFilters, sqlData)

    return execMultiRequests(DB_PATH, cmds)


@app.put("/{dataType}/{pk}", status_code=status.HTTP_204_NO_CONTENT,  summary="Update an existing record")
def updateRecord(dataType, pk, data):
    """
    update a record from the specified table.

    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param pk: Primary key of the record to update
    :type pk: str
    :param data: Fields to update
    :type data: LogIn
    """
    recordDict = logInToDict(data, dataType)
    primaryColumn = getPrimaryColumn(DB_PATH, dataType)

    # ensure PK in dict
    if not recordDict[primaryColumn] == pk:
        raise ValueError(f'given data does not match : {pk}')

    try:
        updateLine(DB_PATH, dataType, recordDict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return getUnSerializedValue(dataType, recordDict, True)


print("Registered routes →", [route.path for route in app.routes])


# def simulateServerRequest(filters):
#     """
#     Simulate a FastAPI request to test dynamicRequest locally with filters.
#
#     :param filters: Dictionary of query parameters.
#     :type filters: dict
#     """
#     import pprint
#
#     queryString = '&'.join(f"{k}={v}" for k, v in filters.items())
#     scope = {
#         'type': 'http',
#         'query_string': queryString.encode('utf-8'),
#         'headers': [],
#     }
#     fakeRequest = Request(scope)
#
#     pprint.pprint(dynamicRequest('machines', fakeRequest))
#
#
# simulateServerRequest({'sector': '1A', 'in_service': 1})
