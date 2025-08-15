"""
===============================================================================
fileName: stringLib
scripter: angiu
creation date: 18/07/2025
description: 
===============================================================================
"""
# ==== native ==== #
import sys

# ==== third ==== #

# ==== local ===== #

# ==== global ==== #
CASES = ['kebab-case', 'snake_case', 'camelCase', 'Train-Case', 'SCREAMING_SNAKE_CASE', 'PascalCase', 'Casual case']


def convertStringToCamelCase(string):
    """
    Convert a string to camelCase.

    :param string: The input string.
    :type string: str

    :return: The camelCase formatted string.
    :rtype: str
    """
    spaceString = string.replace('_', ' ').replace('-', ' ')

    formatedCase = ''
    space = False
    for i, c in enumerate(spaceString):
        if i == 0:
            formatedCase += c.upper()
            continue

        if c == ' ':
            space = True
            continue

        if space:
            formatedCase += c.upper()
        else:
            formatedCase += c

        space = False

    return formatedCase


def formatString(string, convertAs='Casual case'):
    """
    Convert a string to the specified case format.

    :param string: The input string.
    :type string: str
    :param convertAs: The target format (e.g., 'kebab-case', 'snake_case', etc.).
    :type convertAs: str

    :return: The formatted string.
    :rtype: str
    """
    if convertAs not in CASES:
        print(f'not recognize case: {convertAs}')
        sys.exit(1)

    camelCased = convertStringToCamelCase(string)
    if convertAs == 'camelCase':
        return camelCased

    if convertAs in ['kebab-case', 'Train-Case']:
        spacer = '-'
    elif convertAs in ['SCREAMING_SNAKE_CASE', 'snake_case']:
        spacer = '_'
    elif convertAs == 'Casual case':
        spacer = ' '
    else:
        spacer = None

    formated = ''
    for i, c in enumerate(camelCased):
        if i == 0:
            if convertAs in ['kebab-case', 'snake_case', 'camelCase']:
                formated += c.lower()
            elif convertAs in ['Train-Case', 'SCREAMING_SNAKE_CASE', 'PascalCase', 'Casual case']:
                formated += c.upper()

            continue

        if c.isupper():
            if not spacer:
                formated += c
            elif convertAs in ['Train-Case', 'SCREAMING_SNAKE_CASE', 'PascalCase']:
                formated += f'{spacer}{c.upper()}'
            else:
                formated += f'{spacer}{c.lower()}'

            continue

        formated += c

    return formated
