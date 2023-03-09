# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 21:30:36 2020

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from xml.etree import cElementTree as et

from mt_metadata.base.helpers import write_lines, element_to_string
from mt_metadata.base import get_schema, Base
from .standards import SCHEMA_FN_PATHS

# =============================================================================
attr_dict = get_schema("orientation", SCHEMA_FN_PATHS)
# =============================================================================


class Orientation(Base):
    __doc__ = write_lines(attr_dict)

    def __init__(self, **kwargs):

        super().__init__(attr_dict=attr_dict, **kwargs)

    def to_xml(self, string=False, required=True):
        """
        Overwrite to XML to follow EMTF XML format

        :param string: DESCRIPTION, defaults to False
        :type string: TYPE, optional
        :param required: DESCRIPTION, defaults to True
        :type required: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        if self.layout == "orthogonal":
            root = et.Element(
                self.__class__.__name__.capitalize(),
                {
                    "angle_to_geographic_north": f"{self.angle_to_geographic_north:.3f}"
                },
            )
            root.text = self.layout
        else:
            root = et.Element(self.__class__.__name__.capitalize())
            root.text = self.layout

        if not string:
            return root
        else:
            return element_to_string(root)
