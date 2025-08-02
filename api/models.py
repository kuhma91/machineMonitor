"""
===============================================================================
fileName: models.py
scripter: angiu
creation date: 29/07/2025
description:
    Pydantic valide et convertit automatiquement les données entrantes/sortantes.
    Pour que FastAPI sache à quoi s’attendre dans le corps des requêtes POST/PUT, et comment renvoyer les objets en JSON.
    Ça génère aussi la documentation interactive (/docs) avec les schémas JSON.
===============================================================================
"""
# ==== native ==== #

# ==== third ==== #
from pydantic import BaseModel
from typing import Optional

# ==== local ===== #

# ==== global ==== #


class Machine(BaseModel):
    name: str
    sector: str
    serial_number: str
    manufacturer: str
    usage: str
    year_of_acquisition: int
    in_service: bool
    comment: str | None = None


class Log(BaseModel):
    uuid: str
    machineName: str
    type: str
    project: str
    timeStamp: str
    userName: str
    comment: str | None = None
    modifications: list[tuple[str,str]] | None = None


class Employ(BaseModel):
    token: str
    first_name: str
    last_name: str
    trigram: str
    authorisation: str


class MachineIn(BaseModel):
    name: str
    sector: str
    serial_number: str
    manufacturer: str
    usage: str
    year_of_acquisition: int
    in_service: bool
    comment: Optional[str] = None


class LogIn(BaseModel):
    machineName: str
    type: str
    project: str
    comment: Optional[str] = None


class EmployIn(BaseModel):
    token: str
    first_name: str
    last_name: str
    trigram: str
    authorisation: str