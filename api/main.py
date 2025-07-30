"""
===============================================================================
fileName: main.py
scripter: angiu
creation date: 29/07/2025
description: 
===============================================================================
"""
# ==== native ==== #

# ==== third ==== #
from fastapi import FastAPI
from fastapi import status
from fastapi import Request
from fastapi import HTTPException

# ==== local ===== #
from machineMonitor.library.general.sqlLib import getPrimaryColumn
from machineMonitor.library.general.sqlLib import updateLine
from machineMonitor.library.general.sqlLib import createLine
from machineMonitor.library.general.sqlLib import deleteLine
from machineMonitor.api.core import getUnSerializedValue
from machineMonitor.api.core import logInToDict
from machineMonitor.api.core import getInfo
from machineMonitor.api.core import DB_PATH

# ==== global ==== #
print(f"Loading FastAPI app from: {__file__}")

app = FastAPI()  # lowerCase -> conventional


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


@app.get("/{dataType}", response_model=list, summary="Search machines")
def getData(dataType, request):
    """
    Retrieve machines with optional filters from query string.

    :param dataType: Name of the table ('machines' or 'logs').
    :type dataType: str
    :param request: FastAPI request object containing query_params.
    :type request: Request

    :return: List of Machine instances matching filters.
    :rtype: list[Machine]
    """
    # convert all query parameters into a simple dict of filters
    filters = dict(request.query_params)  # request.query_params is a MultiDict
    try:
        return getInfo(dataType, filters)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/{dataType}/{data}", status_code=status.HTTP_204_NO_CONTENT,  summary="Update an existing record")
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
