#!/usr/bin/env python3
"""
init_db.py

Initialize a local SQLite database for MachineMonitor.
Creates the tables `machines` and `logs` if they don’t exist.
"""

import sqlite3
import os

# 1. db based on this module path
DB_PATH = os.path.join(os.path.split(__file__)[0], "machineMonitor.db")


# DLL : Data Definition Language
DLL = '''
CREATE TABLE IF NOT EXISTS machines (
    name TEXT PRIMARY KEY,
    comment TEXT,
    in_service BOOLEAN NOT NULL,
    manufacturer TEXT NOT NULL,
    sector TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    usage TEXT NOT NULL,
    year_of_acquisition INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS logs(
    uuid TEXT PRIMARY KEY,
    comment TEXT,
    machineName TEXT NOT NULL,
    project TEXT NOT NULL,
    timeStamp TEXT NOT NULL,
    type TEXT NOT NULL,
    userName TEXT NOT NULL,
    modifications TEXT,
    FOREIGN KEY(machineName) REFERENCES machines(name),
    FOREIGN KEY(userName) REFERENCES employs(trigram)
);


CREATE TABLE IF NOT EXISTS employs(
    trigram TEXT PRIMARY KEY,
    token TEXT,
    first_name TEXT,
    last_name TEXT,
    authorisation TEXT
);
'''


def main():
    conn = sqlite3.connect(DB_PATH)  # open or create dataBase
    try:
        conn.executescript(DLL)  # exec DLL
        conn.commit()  # valid changes
        print(f"[OK] Database initialized at {DB_PATH}")
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to initialize database: {e}")
    finally:
        conn.close()  # en connection

if __name__ == "__main__":
    main()
