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
from datetime import datetime

# ==== third ==== #
from machineMonitor.api.models import Machine
from machineMonitor.api.models import MachineIn
from machineMonitor.api.models import Log
from machineMonitor.api.models import LogIn

# ==== local ===== #
from machineMonitor.library.general.sqlLib import getPrimaryColumn
from machineMonitor.library.general.sqlLib import getTableFromDb
from machineMonitor.library.general.sqlLib import getRowAsDict
from machineMonitor.library.general.sqlLib import getAllRows
from machineMonitor.library.general.infoLib import getUUID

# ==== global ==== #
PACKAGE_REPO = os.sep.join(__file__.split(os.sep)[:-2])
DB_PATH = os.path.join(PACKAGE_REPO, 'data', 'machineMonitor.db')
MATCHING_OUT_TYPES = {'machines': Machine, 'logs': Log}
MATCHING_IN_TYPES = {'machines': MachineIn, 'logs': LogIn}


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
        raise ValueError(f'no primeKey found in : {DB_PATH} -> {dataType}')

    dataTypes = getTableFromDb(DB_PATH)
    if not dataTypes:
        raise ValueError(f'no data types found in : {DB_PATH}')

    if dataType not in dataTypes:
        raise ValueError(f'{dataType} not in : {DB_PATH}')

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