"""
===============================================================================
fileName: info
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import uuid
# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
COLORS = {
    "blue": (66, 133, 244),
    "red": (234, 67, 53),
    "yellow": (251, 188, 5),
    "green": (52, 168, 83)
}


def getUUID(logsRepo=None):
    """
    Generate a new UUID string and ensure it does not collide with existing files in LOGS_REPO.

    :param logsRepo: folder to verify existing logs from
    :type logsRepo: str

    :return: A unique UUID as a string.
    :rtype: str
    """
    newId = str(uuid.uuid4())
    if not logsRepo or not os.path.exists(logsRepo):
        return newId

    uuids = {os.path.splitext(x)[0] for x in os.listdir(logsRepo)}
    while newId in uuids:
        newId = str(uuid.uuid4())

    return newId