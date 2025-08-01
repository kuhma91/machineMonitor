"""
===============================================================================
fileName: machineMonitor.tokenManager.core
scripter: angiu
creation date: 01/08/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os
import json
import random
import secrets

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
BASE_FOLDER = os.sep.join(__file__.split(os.sep)[:-2])
ICON_FOLDER = os.path.join(BASE_FOLDER, 'icon')
USER_DATA = os.path.join(BASE_FOLDER, 'data', 'users', f'employs.json')
TOKEN_BUTTONS = ['new']
AUTHORISATIONS = ['operator', 'lead', 'supervisor']
TOKEN_LENGTH = 32


def generateToken():
    """
    Generate a random hexadecimal token of specified length.

    :return: Generated token as a hexadecimal string.
    :rtype: str
    """
    return secrets.token_hex(TOKEN_LENGTH)


def generateTrigram(firstName, lastName):
    """
    Generate a unique 3-letter trigram using the first letter of the surname
    and the first two letters of the name.

    :param firstName: First name of the user.
    :type firstName: str
    :param lastName: Last name of the user.
    :type lastName: str

    :return: Unique 3-letter trigram or None if inputs too short.
    :rtype: str
    """
    if len(firstName) < 1 or len(lastName) < 2:
        return None

    trigram = (firstName[0] + lastName[:2]).lower()
    existing = {v.get('trigram', '') for v in getUsers().values()}
    if trigram not in existing:
        return trigram

    attempts = 0
    while attempts < 100:
        altTrigram = (firstName[0] + random.choice(lastName) + random.choice(lastName)).lower()
        if altTrigram not in existing:
            return altTrigram

        attempts += 1

    return None


def getUsers():
    """
    Load user data from the USER_DATA JSON file.

    :return: user data, or empty dict if file doesn't exist.
    :rtype: dict
    """
    if not os.path.exists(USER_DATA):
        return {}

    with open(USER_DATA, 'r', encoding='utf-8') as f:
        return json.load(f)


def saveData(newValue, relatedData):
    """
    Save or update user data in the USER_DATA JSON file.

    :param newValue: Key to identify the user entry.
    :type newValue: str
    :param relatedData: Dictionary containing the user-related data.
    :type relatedData: dict
    """
    currentData = getUsers()

    folder = os.path.split(USER_DATA)[0]
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f'created : {folder}')

    currentData[newValue] = relatedData

    try:
        with open(USER_DATA, 'w', encoding='utf-8') as f:
            json.dump(currentData, f)
            print(f'saved : {newValue}')

    except Exception as e:
        print(f'fail to save : {newValue} -> {e}')