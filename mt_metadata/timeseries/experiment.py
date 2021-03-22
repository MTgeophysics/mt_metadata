# -*- coding: utf-8 -*-
"""
Containers for the full metadata tree

Experiment
   |--> Surveys
   -------------
       |--> Stations
       --------------
           |--> Runs
           -----------
               |--> Channels
               ---------------
                   |--> Responses
                   
Each level has a list attribute 
    
Created on Mon Feb  8 21:25:40 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from xml.etree import cElementTree as et

from . import Auxiliary, Electric, Magnetic, Run, Station, Survey
from .filters import PoleZeroFilter, CoefficientFilter, TimeDelayFilter
from mt_metadata.utils.mt_logger import setup_logger
from mt_metadata.base import helpers

# =============================================================================


class Experiment:
    """
    Top level of the metadata
    """

    def __init__(self, surveys=[]):
        self.logger = setup_logger(f"{__name__}.{self.__class__.__name__}")
        self.surveys = surveys

    def __str__(self):
        lines = ["Experiment Contents", "-" * 20]
        if len(self.surveys) > 0:
            lines.append(f"Number of Surveys: {len(self.surveys)}")
            for survey in self.surveys:
                lines.append(f"\tSurvey ID: {survey.survey_id}")
                lines.append(f"\tNumber of Stations: {len(survey)}")
                lines.append(f"\t{'-' * 20}")
                for station in survey.stations:
                    lines.append(f"\t\tStation ID: {station.id}")
                    lines.append(f"\t\tNumber of Runs: {len(station)}")
                    lines.append(f"\t\t{'-' * 20}")
                    for run in station.runs:
                        lines.append(f"\t\t\tRun ID: {run.id}")
                        lines.append(f"\t\t\tNumber of Channels: {len(run)}")
                        lines.append(
                            "\t\t\tRecorded Channels: "
                            + ", ".join(run.channels_recorded_all)
                        )
                        lines.append(f"\t\t\t{'-' * 20}")

        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, Experiment):
            self.surveys.extend(other.surveys)

            return self
        else:
            msg = f"Can only merge Experiment objects, not {type(other)}"
            self.logger.error(msg)
            raise TypeError(msg)

    def __len__(self):
        return len(self.surveys)

    @property
    def surveys(self):
        """ Return survey list """
        return self._surveys

    @surveys.setter
    def surveys(self, value):
        """ set the survey list """
        if not hasattr(value, "__iter__"):
            msg = (
                "input surveys must be an iterable, should be a list "
                f"not {type(value)}"
            )
            self.logger.error(msg)
            raise TypeError(msg)
        surveys = []
        fails = []
        for ii, survey in enumerate(value):
            if not isinstance(survey, Survey):
                msg = f"Item {ii} is not type(Survey); type={type(survey)}"
                fails.append(msg)
                self.logger.error(msg)
            else:
                surveys.append(survey)
        if len(fails) > 0:
            raise TypeError("\n".join(fails))

        self._surveys = surveys

    @property
    def survey_names(self):
        """ Return names of surveys in experiment """
        return [ss.survey_id for ss in self.surveys]

    def to_xml(self, fn=None, required=True):
        """
        Write XML version of the experiment
        
        :param fn: DESCRIPTION
        :type fn: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        experiment_element = et.Element(self.__class__.__name__)
        for survey in self.surveys:
            survey.update_bounding_box()
            survey.update_time_period()
            survey_element = survey.to_xml(required=required)
            filter_element = et.SubElement(survey_element, "filters")
            for key, value in survey.filters.items():
                filter_element.append(value.to_xml(required=required))
            for station in survey.stations:
                station.update_time_period()
                station_element = station.to_xml(required=required)
                for run in station.runs:
                    run.update_time_period()
                    run_element = run.to_xml(required=required)
                    for channel in run.channels:
                        run_element.append(channel.to_xml(required=required))
                    station_element.append(run_element)
                survey_element.append(station_element)
            experiment_element.append(survey_element)

        if fn:
            with open(fn, "w") as fid:
                fid.write(helpers.element_to_string(experiment_element))
        return experiment_element

    def to_json(self, fn):
        """
        Write JSON version of the experiment
        
        :param fn: DESCRIPTION
        :type fn: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        pass

    def to_pickle(self, fn):
        """
        Write a pickle version of the experiment
        
        :param fn: DESCRIPTION
        :type fn: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        pass

    def from_xml(self, fn=None, element=None):
        """
        
        :param fn: DESCRIPTION, defaults to None
        :type fn: TYPE, optional
        :param element: DESCRIPTION, defaults to None
        :type element: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if fn:
            experiment = et.parse(fn).getroot()
        if element:
            experiment = element

        for survey in list(experiment):
            survey_obj = Survey()
            survey_obj.from_xml(survey)
            for filter_element in survey.findall("filters"):
                survey_obj.filters.update(self._read_filter_element(filter_element)) 
            for station in survey.findall("station"):
                station_obj = Station()
                station_obj.from_xml(station)
                for run in station.findall("run"):
                    run_obj = Run()
                    run_obj.from_xml(run)
                    for channel in run.findall("electric"):
                        ch = Electric()
                        ch.from_xml(channel)
                        run_obj.add_channel(ch)
                    for channel in run.findall("magnetic"):
                        ch = Magnetic()
                        ch.from_xml(channel)
                        run_obj.add_channel(ch)
                    for channel in run.findall("auxiliary"):
                        ch = Auxiliary()
                        ch.from_xml(channel)
                        run_obj.add_channel(ch)
                    station_obj.add_run(run_obj)
                survey_obj.stations.append(station_obj)
            self.surveys.append(survey_obj)

    def from_json(self, fn):
        """
        Read JSON version of experiment
        
        :param fn: DESCRIPTION
        :type fn: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        pass

    def from_pickle(self, fn):
        """
        Read pickle version of experiment
        
        :param fn: DESCRIPTION
        :type fn: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        pass

    def validate_experiment(self):
        """
        Validate experiment is legal
        
        :return: DESCRIPTION
        :rtype: TYPE

        """
        pass
    
    def _read_filter_element(self, filters_element):
        """
        Read in filter element an put it in the correct object
        
        :param filter_element: DESCRIPTION
        :type filter_element: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        filters_dict = {}
        for zpk_element in filters_element.findall("pole_zero_filter"):
            zpk_filter = PoleZeroFilter()
            zpk_filter.from_xml(zpk_element)
            filters_dict[zpk_filter.name] = zpk_filter
            
        for co_element in filters_element.findall("coefficient_filter"):
            co_filter = CoefficientFilter()
            co_filter.from_xml(co_element)
            filters_dict[co_filter.name] = co_filter
            
        for td_element in filters_element.findall("time_delay_filter"):
            td_filter = CoefficientFilter()
            td_filter.from_xml(co_element)
            filters_dict[td_filter.name] = td_filter
            
        return filters_dict
            
