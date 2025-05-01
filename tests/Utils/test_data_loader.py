import unittest
from unittest.mock import patch, mock_open, MagicMock
from Utils import data_loader
import builtins


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Reset _ISSUES before each test to avoid cache effect
        data_loader._ISSUES = None

    @patch('Utils.data_loader.config')
    def test_init(self, mock_config):
        # Mock config return value
        mock_config.get_parameter.return_value = 'fake_path.json'
        loader = data_loader.DataLoader()
        self.assertEqual(loader.data_path, 'fake_path.json')
        mock_config.get_parameter.assert_called_once_with('ENPM611_PROJECT_DATA_PATH')

    @patch('Utils.data_loader.config')
    @patch('Utils.data_loader.DataLoader._load')
    def test_get_issues_first_time(self, mock_load, mock_config):
        # First time _ISSUES is None → _load should be called
        mock_config.get_parameter.return_value = 'fake_path.json'
        mock_load.return_value = ['issue1', 'issue2']

        loader = data_loader.DataLoader()
        issues = loader.get_issues()

        self.assertEqual(issues, ['issue1', 'issue2'])
        mock_load.assert_called_once()

    @patch('Utils.data_loader.config')
    @patch('Utils.data_loader.DataLoader._load')
    def test_get_issues_cached(self, mock_load, mock_config):
        # Already loaded → _load should NOT be called again
        mock_config.get_parameter.return_value = 'fake_path.json'
        data_loader._ISSUES = ['cached_issue']

        loader = data_loader.DataLoader()
        issues = loader.get_issues()

        self.assertEqual(issues, ['cached_issue'])
        mock_load.assert_not_called()

    @patch('Utils.data_loader.config')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"id": 1}, {"id": 2}]')
    @patch('Utils.data_loader.Issue')
    def test_load(self, mock_issue, mock_open_file, mock_config):
        # Test _load loads issues from file and creates Issue objects
        mock_config.get_parameter.return_value = 'fake_path.json'
        mock_issue.side_effect = lambda x: x  # Return the dict directly

        loader = data_loader.DataLoader()
        result = loader._load()

        self.assertEqual(result, [{"id": 1}, {"id": 2}])
        mock_open_file.assert_called_once_with('fake_path.json', 'r')
        self.assertEqual(mock_issue.call_count, 2)


if __name__ == '__main__':
    unittest.main()
