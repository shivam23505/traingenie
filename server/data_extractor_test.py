import unittest
from unittest.mock import patch, mock_open
from data_extractor import GetTrainDataFromIndianRailInfo, GetBodyFromJson, GetTrainInfoFromHtml

class TestDataExtractor(unittest.TestCase):

    @patch('data_extractor.get')
    def test_GetTrainDataFromIndianRailInfo(self, mock_get):
        mock_get.return_value.json.return_value = {'TableContent': '<html>test</html>'}
        result = GetTrainDataFromIndianRailInfo(1)
        self.assertEqual(result, '<html>test</html>')

    @patch('data_extractor.get')
    def test_GetTrainDataFromIndianRailInfo_no_table_content(self, mock_get):
        mock_get.return_value.json.return_value = {}
        result = GetTrainDataFromIndianRailInfo(1)
        self.assertIsNone(result)

    @patch('builtins.open', new_callable=mock_open, read_data='{"TableContent": "<html>test</html>"}')
    def test_GetBodyFromJson(self, mock_file):
        result = GetBodyFromJson('dummy_file.json')
        self.assertEqual(result, '<html>test</html>')

    def test_GetTrainInfoFromHtml(self):
        html_data = """<div>
                <div>12345</div>
                <div>TestTrain</div>
                <div>Express</div>
                <div>NR</div>
                <div>01-01-2020</div>
                <div>01-01-2021</div>
                <div>Source</div>
                <div>10:00</div>
                <div>Destination</div>
                <div>20:00</div>
                <div>10h</div>
                <div>5</div>
                <div>Daily</div>
                <div>1A,2A</div>
                <div>1000</div>
                <div>100</div>
                <div>54321</div>
        </div>
        """
        result = GetTrainInfoFromHtml(html_data.replace(' ', '').replace('\n', ''))
        expected = {
            '12345': {
                'train_number': '12345',
                'train_name': 'TestTrain',
                'train_type': 'Express',
                'train_zone': 'NR',
                'source': 'Source',
                'source_time': '10:00',
                'dest': 'Destination',
                'dest_time': '20:00',
                'duration': '10h',
                'halts': '5',
                'days': 'Daily',
                'classes': '1A,2A',
                'distance': '1000',
                'speed': '100',
                'return_train_number': '54321'
            }
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()