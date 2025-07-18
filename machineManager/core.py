"""
===============================================================================
fileName: machineMonitor.machineManager.core
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import os

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
ICON_FOLDER = os.path.join(os.sep.join(__file__.split(os.sep)[:-2]), 'icon')
NEEDED_INFOS = {'secteur': ['1A', '1B', '1C', '2A', '2B', '2C'],
                'type': ['CNC', 'decoupe laser', 'imprimantes 3D'],
                'constructeur': None,
                'numero de serie': None,
                "annee d'acquisition": None,
                'en service': True}