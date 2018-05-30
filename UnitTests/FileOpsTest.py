import unittest

from BusinessLogic.FileOps import *

class TestFileOps(unittest.TestCase):

    def test_ConvertFileNameToMeaningful(self):

        name = ConvertFileNameToMeaningful("TerrorisAttacksIndiaYears.json")
        self.assertEqual(name , "Terroris Attacks India Years")

        name = ConvertFileNameToMeaningful("StateWiseTreeCover.json")
        self.assertEqual(name , "State Wise Tree Cover")

        name = ConvertFileNameToMeaningful("StateWiseReasonsForNotUsingGovtHealthFacilities.json")
        self.assertEqual(name , "State Wise Reasons For Not Using Govt Health Facilities")

        name = ConvertFileNameToMeaningful("LocationWiseStateNumberOfOngoingProjects.json")
        self.assertEqual(name , "Location Wise State Number Of Ongoing Projects")

        name = ConvertFileNameToMeaningful("StateWiseHIV.json")
        self.assertEqual(name , "State Wise HIV")
        