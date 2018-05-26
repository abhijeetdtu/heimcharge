import unittest

from PresentationLayer.Visualization.ChartPlot import *

class TestGetFilterArrayFromArguments(unittest.TestCase):

    def test_GetFilterArrayFromArgumentsReturnsCorrectly(self):
        filterArr = GetFilterArrayFromArguments(['1>6' , '4<7' , '7!=10' ,'567==Mayanmar'])
        self.assertEqual(len(filterArr), 4)
        self.assertEqual(filterArr[0].dfColIndex, 1)
        self.assertEqual(filterArr[0].op, '>')
        self.assertEqual(filterArr[0].value, '6')

        self.assertEqual(filterArr[1].dfColIndex, 4)
        self.assertEqual(filterArr[1].op, '<')
        self.assertEqual(filterArr[1].value, '7')

        self.assertEqual(filterArr[2].dfColIndex, 7)
        self.assertEqual(filterArr[2].op, '!=')
        self.assertEqual(filterArr[2].value, '10')

        self.assertEqual(filterArr[3].dfColIndex, 567)
        self.assertEqual(filterArr[3].op, '==')
        self.assertEqual(filterArr[3].value, 'Mayanmar')

    def test_CorrectBlueprintSubstring(self):
        blueprintUrl = '/plotwithMap/'
        url_prefix = '/india'
        url = '{0}{1}'.format( url_prefix , blueprintUrl)
        
        calcPrefix = url[:url.find(blueprintUrl)]
        self.assertEqual(calcPrefix,url_prefix)

if __name__ == '__main__':
    unittest.main()