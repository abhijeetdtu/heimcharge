import unittest

from BusinessLogic.GeoOps import *
from BusinessLogic.FileOps import *

class TestGeoOps(unittest.TestCase):

    def test_GetLocationLatLongReturnsAList(self):

        lat,long = GetLocationLatLong("Mumbai, india")
        self.assertIsNotNone(lat)
        self.assertIsNotNone(long)

    def test_AddLatLongColumnsToDataframeCorrectyAddsTwoColumns(self):

        df,columns = GetDataFrame("StateWiseSEZ")
        df = AddLatLongColumnsToDataframe(df,"States/UT")

        self.assertIsNotNone(df["Lat"])
        self.assertIsNotNone(df["Long"])