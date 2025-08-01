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
EMPLOYS_FOLDER = os.path.join(BASE_FOLDER, 'data', 'employs')
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
    Load user data from the USER_FOLDER path

    :return: user data, or empty dict if file doesn't exist.
    :rtype: dict
    """
    if not os.path.exists(EMPLOYS_FOLDER):
        return {}

    data = {}
    for name in os.listdir(EMPLOYS_FOLDER):
        if not name.endswith('.json'):
            continue

        shortName = os.path.splitext(name)[0]
        jsonPath = os.path.join(EMPLOYS_FOLDER, name)
        with open(jsonPath, 'r', encoding='utf-8') as f:
            data[shortName] = json.load(f)

    return data


def saveData(newValue, relatedData):
    """
    Save or update user data in the EMPLOYS_FOLDER JSON file.

    :param newValue: Key to identify the user entry.
    :type newValue: str
    :param relatedData: Dictionary containing the user-related data.
    :type relatedData: dict
    """
    if not os.path.exists(EMPLOYS_FOLDER):
        os.makedirs(EMPLOYS_FOLDER)
        print(f'created : {EMPLOYS_FOLDER}')

    jsonPath = os.path.join(EMPLOYS_FOLDER, f'{newValue}.json')
    try:
        with open(jsonPath, 'w', encoding='utf-8') as f:
            json.dump(relatedData, f)
            print(f'saved : {newValue}')

    except Exception as e:
        print(f'fail to save : {newValue} -> {e}')
