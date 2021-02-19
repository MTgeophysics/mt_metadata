# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 12:49:13 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from mt_metadata.timeseries.stationxml.fdsn_tools import release_dict

from mt_metadata import timeseries as metadata
from mt_metadata.timeseries.stationxml.utils import BaseTranslator

from obspy.core import inventory

# =============================================================================


class XMLStationMTStation(BaseTranslator):
    """
    translate back and forth between StationXML Station and MT Station
    """

    def __init__(self):
        super().__init__()

        self.xml_translator.update(
            {
                "alternate_code": "id",
                "channels": None,
                "code": "fdsn.id",
                "comments": "provenance.comments",
                "creation_date": "time_period.start",
                "data_availability": None,
                "description": "comments",
                "elevation": "location.elevation",
                "end_date": "time_period.end",
                "equipments": None,
                "external_references": None,
                "geology": None,
                "identifiers": None,
                "latitude": "location.latitude",
                "longitude": "location.longitude",
                "operators": "special",
                "site": "special",
                "start_date": "time_period.start",
                "termination_date": "time_period.end",
                "vault": None,
                "water_level": None,
                "restricted_status": "special",
            }
        )

        # StationXML to MT Survey
        self.mt_translator = self.flip_dict(self.xml_translator)
        self.mt_translator["geographic_name"] = "site"
        self.mt_translator["provenance.comments"] = None
        self.mt_translator["time_period.start"] = "start_date"
        self.mt_translator["time_period.end"] = "end_date"

        self.mt_comments_list = [
            "run_list",
            "orientation.method",
            "orientation.reference_frame",
            "location.declination.value",
            "location.declination.model",
            "location.declination.comments",
            "provenance.software.author",
            "provenance.software.name",
            "provenance.software.version",
            "provenance.comments"
            
        ]
        
    def xml_to_mt(self, xml_station):
        """
        Translate a StationXML station object to MT Survey object

        :param station: StationXML station element
        :type station: :class:`obspy.core.inventory.station`

        """

        if not isinstance(xml_station, inventory.Station):
            msg = (
                f"Input must be obspy.core.inventory.station object not {type(xml_station)}"
            )
            self.logger.error(msg)
            raise ValueError(msg)

        mt_station = metadata.Station()
        run_comments = []

        for mt_key, xml_key in self.mt_translator.items():
            if xml_key is None:
                continue
            if xml_key in ["site"]:
                site = xml_station.site
                mt_station.geographic_name = site.name
            
            elif mt_key in ["comments"]:
                for comment in xml_station.comments:
                    key, value = self.read_xml_comment(comment)
                    if "mt.run" in key:
                        run_comments.append({key: value})
                        continue
                    
                    key = key.split("mt.station.")[1]
                    if "summary" in key:
                        key = key.replace("summary", "comments")
                    if key in ["comments"]:
                        if mt_station.comments:
                            mt_station.comments += value
                        else:
                            mt_station.comments = value
                    else:
                        mt_station.set_attr_from_name(key, value)

            else:
                value = getattr(xml_station, xml_key)
                if value is None:
                    continue
                if isinstance(value, (list, tuple)):
                    for k, v in zip(mt_key, value):
                        mt_station.set_attr_from_name(k, v)
                else:
                    if xml_key == "restricted_status":
                        value = self.flip_dict(release_dict)[value]
                    if "time_period" in mt_key:
                        value = value.isoformat()
                    
                mt_station.set_attr_from_name(mt_key, value)
        
        return mt_station, run_comments
                
    def mt_to_xml(self, mt_station):
        """
        Convert MT Survey to Obspy Network
        
        .. note:: For now the default code is ZU which is an IRIS catch-all network
        
        """
        if not isinstance(mt_station, metadata.Station):
            msg = (
                f"Input must be mt_metadata.timeseries.Station object not {type(mt_station)}"
            )
            self.logger.error(msg)
            raise ValueError(msg)
        
        if mt_station.id is None:
            if mt_station.fdsn.id is None:
                msg = "Need to input id or fdsn.id, both cannot be None"
                self.logger.error(msg)
                raise ValueError(msg)
            else:
                code = mt_station.fdsn.id
        else:
            code = inventory.Station(mt_station.id)
            
        xml_station = inventory.Station(code, 
                                        mt_station.location.latitude,
                                        mt_station.location.longitude,
                                        mt_station.location.elevation)

        for xml_key, mt_key in self.xml_translator.items():
            print(xml_key, mt_key)
            if mt_key is None:
                msg = "cannot currently map mt_key.station to inventory.station.{0}".format(
                    xml_key
                )
                self.logger.debug(msg)
                continue
            if xml_key == "operators":
                if mt_station.acquired_by.author is not None:
                    operator = inventory.Operator(
                        agency=mt_station.acquired_by.organization
                    )
                    person = inventory.Person(names=[mt_station.acquired_by.author])
                    operator.contacts = [person]
                    xml_station.operators = [operator]

            elif xml_key == "site":
                xml_station.site.description = mt_station.geographic_name
                xml_station.site.name = mt_station.id

            elif xml_key == "comments":
                if mt_station.comments is not None:
                    comment = inventory.Comment(mt_station.comments, id=0)
                    xml_station.comments.append(comment)
            else:
                setattr(xml_station, xml_key, mt_station.get_attr_from_name(mt_key))

