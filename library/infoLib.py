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
import ast
import sys
import site
import importlib.util
import sysconfig

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
PACKAGE_PATH = os.sep.join(__file__.split(os.sep)[:-2])
NEEDED = ['uvicorn', 'flake8', 'pytest', 'httpx']
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

def getLibraryModules():
    """
    Retrieve the set of Python standard library module names.

    Uses sys.stdlib_module_names if available (Python ≥3.10); otherwise scans the stdlib directory.

    :return: Set of standard library module names.
    :rtype: set
    """
    stdlibNames = getattr(sys, 'stdlib_module_names', None)
    if stdlibNames is None:
        stdlib_path = sysconfig.get_paths()['stdlib']

        names = []
        for entry in os.listdir(stdlib_path):
            if entry.endswith('.py'):
                names.append(entry[:-3])

            elif os.path.isdir(os.path.join(stdlib_path, entry)):
                names.append(entry)

        stdlibNames = set(names)

    return stdlibNames


def getImportType(moduleName, projectRoot):
    """
    Determines the type of a module: standard library, third-party, local, or unknown.

    :param moduleName: Name of the module to check.
    :type moduleName: str
    :param projectRoot: Absolute path to the root of the project.
    :type projectRoot: str

    :return: The type of the module: 'standard', 'third', 'local', or 'unknown'.
    :rtype: str
    """
    spec = importlib.util.find_spec(moduleName)
    if not spec or not spec.origin:
        return "unknown"

    # nom dans la stdlib → standard
    if moduleName in getLibraryModules() or spec.origin == 'built-in':
        return "standard"

    origin = os.path.realpath(spec.origin)
    prj = os.path.realpath(projectRoot)

    # local under project root
    if origin.startswith(prj):
        return "local"

    # repères site-packages / purelib / platlib / user-site
    lib_paths = set()
    for key in ('purelib', 'platlib'):
        p = sysconfig.get_paths().get(key)
        if p: lib_paths.add(os.path.realpath(p))
    lib_paths.update(os.path.realpath(p) for p in site.getsitepackages())
    lib_paths.add(os.path.realpath(site.getusersitepackages()))

    if any(origin.startswith(p) for p in lib_paths):
        return "third"

    return "unknown"


def getImportsFromFile(filePath, projectRoot):
    """
    Parses a Python file to extract imported modules and classify their origin.

    :param filePath: Path to the Python file to analyze.
    :type filePath: str
    :param projectRoot: Absolute path to the root of the project for detecting local imports.
    :type projectRoot: str

    :return: imported module to its type ('standard', 'third-party', 'local', or 'unknown').
    :rtype: dict
    """
    with open(filePath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filePath)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split('.')[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split('.')[0])

    result = {}
    for imp in imports:
        importType = getImportType(imp, projectRoot)
        result.setdefault(importType, []).append(imp)

    return {k: list(set(v)) for k, v in result.items()}


def getFileRecursively(folder, extensions=None, toSkip=None):
    """
    Recursively retrieves file paths from a folder, with optional extension filtering and exclusion by substrings.

    :param folder: Root folder to search files from.
    :type folder: str
    :param extensions: allowed file extensions (e.g., ['.py', '.txt']). If None, all files are included.
    :type extensions: list
    :param toSkip: substrings; files or folders containing any of these will be skipped.
    :type toSkip: list

    :return: file paths found recursively under the folder.
    :rtype: list
    """
    if not os.path.exists(folder):
        return []

    content = []
    for item in os.listdir(folder):
        if toSkip and any(s in item for s in toSkip):
            continue

        itemPath = os.path.join(folder, item)
        if os.path.isfile(itemPath):
            if extensions and os.path.splitext(item)[-1] not in extensions:
                continue

            content.append(itemPath)

        elif os.path.isdir(itemPath):
            content.extend(getFileRecursively(itemPath, extensions, toSkip))

    return content


def getRequirements(skipPrint=False):
    """
    Reads the project's requirements.txt file and returns a list of required packages.

    :return: package names specified in the requirements file.
    :rtype: list
    """
    content = getFileRecursively(PACKAGE_PATH, extensions=['.py'])

    imports = NEEDED
    projectRoot = os.path.split(PACKAGE_PATH)[0]
    for f in content:
        importData = getImportsFromFile(f, projectRoot)
        imports.extend(importData.get('third', []))

    requirements = list(set(imports))

    if not skipPrint:
        for imp in requirements:
            print(imp)

    return requirements
