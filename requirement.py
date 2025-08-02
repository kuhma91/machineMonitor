import os

from machineMonitor.library.infoLib import getFileRecursively
from machineMonitor.library.infoLib import getImportsFromFile
from machineMonitor.library.infoLib import getRequirements
from machineMonitor.library.infoLib import REQUIREMENTS_FILE

PROJECT_ROOT = os.sep.join(__file__.split(os.sep)[:-2])
BASE_REPO = os.path.split(__file__)[0]
NEEDED = ['uvicorn', 'flake8']


def updateRequirements():
    content = getFileRecursively(BASE_REPO, extensions=['.py'])

    imports = NEEDED
    for f in content:
        importData = getImportsFromFile(f, PROJECT_ROOT)
        imports.extend(importData.get('third', []))

    needed = list(set(imports))
    requirements = getRequirements()

    if needed == requirements:
        return

    with open(REQUIREMENTS_FILE, 'w', encoding='utf-8') as f:
        f.writelines('\n'.join(needed))
        print(f'requirement updated : {REQUIREMENTS_FILE}')


if __name__ == '__main__':
    updateRequirements()
