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
from datetime import datetime

# ==== third ==== #
import sqlite3
from fastapi import FastAPI
from fastapi import status
from fastapi import HTTPException

# ==== local ===== #
from machineMonitor.api.models import Machine
from machineMonitor.api.models import Log
from machineMonitor.library.general.sqlLib import getTableFromDb
from machineMonitor.library.general.sqlLib import getPrimaryColumn
from machineMonitor.library.general.sqlLib import syncDatabase
from machineMonitor.library.general.sqlLib import getRowAsDict
from machineMonitor.library.general.infoLib import getUUID

# ==== global ==== #
print(f"🔍 Loading FastAPI app from: {__file__}")

app = FastAPI()  # lowerCase -> conventional
PACKAGE_REPO = os.sep.join(__file__.split(os.sep)[:-2])
DB_PATH = os.path.join(PACKAGE_REPO, 'data', 'machineMonitor.db')
MATCHING_TYPES = {'machines': Machine, 'logs': Log}


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

    primKey = getPrimaryColumn(DB_PATH, dataType)
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


@app.get("/", summary="Read root")  # HTTP GET = request to use root to call function right under the decorator
def read_root():
    # return a simple JSON response
    return {"msg": "OK"}


@app.get("/machines", response_model=list[Machine], summary="List all machines",)
def listMachines():
    """
    Retrieve the list of all machines.

    :return: All machines from the database.
    :rtype: list[Machine]
    """
    records = getInfo("machines")
    return [Machine(**r) for r in records]


@app.get("/machines/{name}", response_model=Machine, summary="Get one machine by name")
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


@app.get("/logs", response_model=list[Log], summary="List all logs")
def listLogs():
    """
    Retrieve all logs.

    :return: All logs from the database.
    :rtype: list[Log]
    """
    records = getInfo("logs")
    return [Log(**r) for r in records]


@app.get("/logs/{uuid}", response_model=Log, summary="Get one log by UUID")
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


@app.post("/machines", response_model=Machine, summary="Create a new machine")
def createMachine(machineData):
    """
    :param machineData: Data provided by the user to create a machine.
    :type machineData: MachineIn

    :return: Full machine record, including generated fields.
    :rtype: Machine
    """
    data = machineData.model_dump()  # Serialize incoming Pydantic model to dict

    # Insert into database (will INSERT or UPDATE as needed)
    try:
        syncDatabase(DB_PATH, {'machines': [data]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Internal Server Error

    # Retrieve the newly created row by its primary key
    row = getRowAsDict(DB_PATH, 'machines', data['name'])
    if not row:
        raise HTTPException(status_code=404, detail="Machine not found after insert")

    return Log(**row)


@app.post("/logs", response_model=Machine, summary="Create a new log")
def createLog(logsData):
    """
    :param logsData: Data provided by the user to create a log.
    :type logsData: MachineIn

    :return: Full log record, including generated fields.
    :rtype: log
    """
    data = logsData.model_dump()  # Serialize incoming Pydantic model to dict

    # Serialize incoming Pydantic model to dict
    data.update({
        'timeStamp': datetime.now().strftime('%Y_%m_%d__%H_%M_%S'),
        'userName': os.getlogin(),
        'uuid': getUUID()
    })

    # Insert into database (will INSERT or UPDATE as needed)
    try:
        syncDatabase(DB_PATH, {'logs': [data]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Internal Server Error

    # Retrieve the newly created row by its primary key
    row = getRowAsDict(DB_PATH, 'logs', data['uuid'])
    if not row:
        raise HTTPException(status_code=404, detail="Machine not found after insert")

    return Log(**row)


@app.delete("/machines/{name}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a machine by name")
def deleteMachin(name):
    """
    Delete a machine record from the database.

    :param name: Primary key (name) of the machine to delete.
    :type name: str

    :return: No content on success.
    :rtype: None
    """
    # connect and open cursor
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # check existence
        cursor.execute(
            "SELECT 1 FROM machines WHERE name = ?;",
            (name,)
        )
        if cursor.fetchone() is None:
            # not found → 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Machine not found"
            )
        # delete the row
        cursor.execute(
            "DELETE FROM machines WHERE name = ?;",
            (name,)
        )
        conn.commit()

    # 204 No Content
    return Response(status_code=status.HTTP_204_NO_CONTENT)


print("📦 Registered routes →", [route.path for route in app.routes])
