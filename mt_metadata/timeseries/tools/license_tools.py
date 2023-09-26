# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 12:59:56 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from types import SimpleNamespace
import json


# =============================================================================
def read_json_to_object(fn):
    """
    read a json file directly into an object

    :param fn: DESCRIPTION
    :type fn: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """

    with open(fn, "r") as fid:
        obj = json.load(fid, object_hook=lambda d: SimpleNamespace(**d))
    return obj


def get_license_names(filename, creative_commons=True, mit=True):
    """
    Get license names from json file

    :param filename: DESCRIPTION
    :type filename: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    filename = Path(filename)

    obj = read_json_to_object(filename)

    names = []
    for item in obj.licenses:
        if creative_commons:
            if item.name.lower().startswith("creative"):
                names.append(item.name)
                names.append(item.licenseId)
        if mit:
            if item.name.lower().startswith("mit"):
                names.append(item.name)
                names.append(item.licenseId)

    return names
