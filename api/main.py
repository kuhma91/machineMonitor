"""
===============================================================================
fileName: main.py
scripter: angiu
creation date: 29/07/2025
description:
    - connexion : uvicorn machineMonitor.api.main:app --reload
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
from machineMonitor.library.general.sqlLib import getAllRows
from machineMonitor.library.general.sqlLib import updateLine
from machineMonitor.library.general.sqlLib import createLine
from machineMonitor.library.general.sqlLib import deleteLine
from machineMonitor.library.general.sqlLib import execMultiRequests
from machineMonitor.api.core import getDataTypesAndColumns
from machineMonitor.api.core import getUnSerializedValue
from machineMonitor.api.core import getAllowedNames
from machineMonitor.api.core import getRequestCmd
from machineMonitor.api.core import logInToDict
from machineMonitor.api.core import hasAccess
from machineMonitor.api.core import DB_PATH
from machineMonitor.api.core import SQL_KEYS

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


@app.get("/ask", response_model=list[dict], summary="search from filters")
def dynamicRequest(credentials=Depends(security), request=None):
    """
    Retrieve machines with optional filters from query string.

    :param credentials: Token credentials extracted from the HTTP Authorization header.
    :type credentials: fastapi.security.HTTPAuthorizationCredentials
    :param request: FastAPI request object containing query_params.
    :type request: Request

    :return: List of Machine instances matching filters.
    :rtype: list[dict]
    """
    if not hasAccess(credentials):
        raise HTTPException(status_code=401, detail="Invalid or missing token")  # unrecognized user

    requestDict = dict(request.query_params)
    tableData = getDataTypesAndColumns(requestDict)
    sqlData = {k: v for k,v in requestDict.items() if k in SQL_KEYS}

    result = []

    cmds = {}
    for table, filtersData in tableData.items():
        if table == 'logs':
            filtersData['userName'] = getAllowedNames(credentials, filtersData)

        if not filtersData:
            result.extend(getAllRows(DB_PATH, table))
            continue

        cmds[table] = getRequestCmd(table, filtersData, sqlData)

    if cmds:
        result.extend(execMultiRequests(DB_PATH, cmds))

    return result


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
