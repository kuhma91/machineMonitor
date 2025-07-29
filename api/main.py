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

# ==== third ==== #
from fastapi import FastAPI
import sqlite3
from fastapi import FastAPI
from fastapi import HTTPException

# ==== local ===== #
from machineMonitor.api.models import Machine
from machineMonitor.api.models import Log
from machineMonitor.library.general.sqlLib import getTableFromDb
from machineMonitor.library.general.sqlLib import getPrimaryKeyValue

# ==== global ==== #
app = FastAPI()  # lowerCase -> conventional
PACKAGE_REPO = os.sep.join(__file__.split(os.sep)[:-2])
DB_PATH = os.path.join(PACKAGE_REPO, 'data', 'machineMonitor.db')
MATCHING_TYPES = {'machines': Machine, 'logs': Log}


@app.get("/")  # HTTP GET = request to use root to call function right under the decorator
def read_root():
    # return a simple JSON response
    return {"msg": "OK"}


def getInfo(dataType, filters=None):
    """
    Retrieve records from a DB table and apply optional filters.

    :param dataType: Name of the table to query.
    :type dataType: str

    :param filters: Dictionary of column names to values for filtering.
    :type filters: dict[str, any]

    :return: List of records as dictionaries.
    :rtype: list[dict]
    """
    dataTypes = getTableFromDb(DB_PATH)
    if not dataTypes:
        raise ValueError(f'no data types found in : {DB_PATH}')

    if dataType not in dataTypes:
        raise ValueError(f'{dataType} not in : {DB_PATH}')

    primKey = getPrimaryKeyValue(DB_PATH, dataType)
    if not primKey:
        raise ValueError(f'no primeKey found in : {DB_PATH} -> {dataType}')

    result = []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # Return rows as dicts: column_name → value
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {dataType};")  # Use parameterized queries to prevent SQL injection
        rows = cursor.fetchall()

    for row in rows:
        obj = MATCHING_TYPES[dataType](**dict(row))  # Instantiate Pydantic model (Machine or Log)
        record = obj.model_dump()  # serialize to dict


        # Apply filters if provided
        if filters and not all(record.get(k) == v for k, v in filters.items()):
            continue

        result.append(record)

    return result


@app.get("/machines", response_model=list[Machine])
def getMachines():
    """
    Retrieve the list of all machines.

    :return: All machines from the database.
    :rtype: list[Machine]
    """
    records = getInfo("machines")
    return [Machine(**r) for r in records]


@app.get("/machines/{name}", response_model=Machine)
def getMachine(name):
    """
    Retrieve a single machine by its name.

    :param name: Primary key of the machine.
    :type name: str

    :return: Machine record matching the name.
    :rtype: Machine
    """
    records = getInfo("machines", filters={"name": name})
    if not records:
        raise HTTPException(status_code=404, detail="Machine not found")
    return Machine(**records[0])


@app.get("/logs", response_model=list[Log])
def getLogs():
    """
    Retrieve all logs.

    :return: All logs from the database.
    :rtype: list[Log]
    """
    records = getInfo("logs")
    return [Log(**r) for r in records]


@app.get("/logs/{uuid}", response_model=Log)
def getLog(uuid):
    """
    Retrieve a single log by its UUID.

    :param uuid: Primary key of the log.
    :type uuid: str

    :return: Log record matching the UUID.
    :rtype: Log
    """
    records = getInfo("logs", filters={"uuid": uuid})
    if not records:
        raise HTTPException(status_code=404, detail="Log not found")
    return Log(**records[0])