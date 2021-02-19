# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 16:33:42 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

import unittest
from mt_metadata.timeseries.stationxml.utils import BaseTranslator
from obspy.core.inventory import Comment


class TestReadXMLComment(unittest.TestCase):
    """
    test reading different comments
    """

    def setUp(self):
        self.run_comment = Comment(
            "author: John Doe, comments: X array a 0 and 90 degrees.",
            subject="mt.run:b.metadata_by",
        )
        self.null_comment = Comment(None, subject="mt.survey.survey_id")
        self.long_comment = Comment("a: b, c: d, efg", subject="mt.run.a:comment")
        
    def test_null_comment(self):
        k, v = BaseTranslator.read_xml_comment(self.null_comment)
        self.assertEqual("mt.survey.survey_id", k)
        self.assertEqual("None", v)
        
    def test_run_comment(self):
        k, v = BaseTranslator.read_xml_comment(self.run_comment)
        self.assertEqual(k, "mt.run:b.metadata_by")
        self.assertIsInstance(v, dict)
        self.assertDictEqual(v, {"author": "John Doe", 
                                 "comments": "X array a 0 and 90 degrees."})
    
    def test_long_comment(self):
        k, v = BaseTranslator.read_xml_comment(self.long_comment)
        self.assertEqual(k, "mt.run.a:comment")
        self.assertIsInstance(v, dict)
        self.assertDictEqual(v, {"a": "b", "c":"d, efg"})
        


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    unittest.main()
