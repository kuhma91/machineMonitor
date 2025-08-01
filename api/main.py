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
from machineMonitor.api.core import MATCHING_OUT_TYPES

# ==== global ==== #
print(f"Loading FastAPI app from: {__file__}")

app = FastAPI()  # lowerCase -> conventional
security = HTTPBearer()  # get token from URL Authorization header


@app.post("/create", status_code=status.HTTP_204_NO_CONTENT,  summary="add line from given type and data")
def createRecord(request):
    """
    add a record from the specified table.

    :param request: FastAPI request object containing query_params.
    :type request: Request
    """
    data = dict(request.query_params)

    tableType = data.get('tableType')
    if not tableType:
        raise HTTPException(status_code=422, detail='missing value : "tableType"')

    model = MATCHING_OUT_TYPES.get(tableType)
    if not model:
        raise HTTPException(status_code=422, detail=f'unknown table: {tableType}')

    try:
        parsed = model(**{k: v for k, v in data.items() if k != 'tableType'})
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    recordData = parsed.dict()

    # Insert into database
    try:
        createLine(DB_PATH, tableType, recordData)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # get new created row
    return getUnSerializedValue(tableType, recordData, True)


@app.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item from given type and primaryKey")
def deleteRecord(request):
    """
    add a record from the specified table.

    :param request: FastAPI request object containing query_params.
    :type request: Request
    """
    data = dict(request.query_params)

    tableType = data.get('tableType')
    if not tableType:
        raise HTTPException(status_code=422, detail='missing : tableType')

    primaryColumn = getPrimaryColumn(DB_PATH, tableType)
    if not primaryColumn:
        raise HTTPException(status_code=422, detail=f'no primary column found for : {tableType}')

    pk = data.get(primaryColumn)
    if not pk:
        raise HTTPException(status_code=422, detail=f'missing primaryColumn un data: {primaryColumn}')

    try:
        deleteLine(DB_PATH, tableType, pk)

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


@app.put("/update", status_code=status.HTTP_204_NO_CONTENT,  summary="Update an existing record")
def updateRecord(request):
    """
    update a record from the specified table.

    :param request: FastAPI request object containing query_params.
    :type request: Request
    """
    data = dict(request.query_params)

    tableType = data.get('tableType')
    if not tableType:
        raise HTTPException(status_code=422, detail='missing : tableType')

    primaryColumn = getPrimaryColumn(DB_PATH, tableType)
    if not primaryColumn:
        raise HTTPException(status_code=422, detail=f'no primary column found for : {tableType}')

    pk = data.get(primaryColumn)
    if not pk:
        raise HTTPException(status_code=422, detail=f'missing primaryColumn un data: {primaryColumn}')

    model = MATCHING_OUT_TYPES.get(tableType)
    if not model:
        raise HTTPException(status_code=422, detail=f'unknown table: {tableType}')

    try:
        parsed = model(**{k: v for k, v in data.items() if k != 'tableType'})
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    recordData = parsed.dict()

    try:
        updateLine(DB_PATH, tableType, recordData)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return getUnSerializedValue(tableType, recordData, True)


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
