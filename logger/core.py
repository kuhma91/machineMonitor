"""
===============================================================================
fileName: machineMonitor.logger.core
scripter: angiu
creation date: 22/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import uuid
import os
import csv
import pprint

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
BASE_FOLDER = os.sep.join(__file__.split(os.sep)[:-2])
DATA_REPO = os.path.join(BASE_FOLDER, 'data')
LOGS_REPO = os.path.join(DATA_REPO, 'logs')
ICON_FOLDER = os.path.join(BASE_FOLDER, 'icon')
AUTHORISATIONS = {'supervisor': ['edit', 'delete'], 'lead': ['edit']}
LOG_TYPES = ['empty consumable & reload', 'info', 'error']


def getEmployeesData():
    """
    Load employee data from the 'employes.csv' file.

    :return: each employee’s trigram to a dict of their fields, or 'user' if the file is missing.
    :rtype: dict
    """
    data = {}

    employeesFile = os.path.join(DATA_REPO, 'employes.csv')
    if not os.path.exists(employeesFile):
        return data

    titles = None
    with open(employeesFile, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for i, row in enumerate(reader):
            if i == 0:
                titles = [x.strip().lower() for x in row]
                continue

            trigramIndex = [x.strip() for x in titles].index('trigram')
            trigram = row[trigramIndex].strip().lower()
            data[trigram] = {x: row[i].strip().lower() for i, x in enumerate(titles)}

    return data


def getAuthorisation():
    """
    Retrieve the authorization level for the current OS user.

    :return: The authorization level from employees data, or 'user' if the user is not found.
    :rtype: str
    """
    user = os.getlogin().lower()
    employeesData = getEmployeesData()

    if user not in employeesData:
        return 'user'

    return employeesData.get(user, {}).get('authorisation', 'user')
