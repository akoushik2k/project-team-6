import unittest
from unittest.mock import patch, Mock
from Utils import data_generator


class TestDataGenerator(unittest.TestCase):

    @patch('Utils.data_generator.requests.get')
    def test_fetch_issue_timeline_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "event": "commented",
                "created_at": "2023-01-01T00:00:00Z",
                "actor": {"login": "user1"},
                "body": "test comment"
            },
            {
                "event": "labeled",
                "created_at": "2023-01-02T00:00:00Z",
                "actor": {"login": "user2"},
                "label": {"name": "bug"}
            },
            {
                "event": "unrelated_event",
                "created_at": "2023-01-03T00:00:00Z",
                "actor": {"login": "user3"}
            },
            "invalid_event_format"
        ]
        mock_get.return_value = mock_response

        result = data_generator.fetch_issue_timeline(1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['event_type'], "commented")
        self.assertEqual(result[1]['event_type'], "labeled")

    @patch('Utils.data_generator.requests.get')
    def test_fetch_issue_timeline_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = data_generator.fetch_issue_timeline(1)
        self.assertEqual(result, [])

    def test_format_issue(self):
        issue = {
            "html_url": "http://example.com",
            "user": {"login": "creator"},
            "labels": [{"name": "bug"}, {"name": "enhancement"}],
            "state": "open",
            "assignees": [{"login": "dev1"}],
            "title": "Issue title",
            "body": "Issue body\r\nNew line",
            "number": 42,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }

        with patch('Utils.data_generator.fetch_issue_timeline', return_value=["dummy_event"]):
            result = data_generator.format_issue(issue)

        self.assertEqual(result['url'], "http://example.com")
        self.assertEqual(result['creator'], "creator")
        self.assertEqual(result['labels'], ["bug", "enhancement"])
        self.assertEqual(result['assignees'], ["dev1"])
        self.assertIn("dummy_event", result['events'])
        self.assertIn("\n", result['text'])

    @patch('Utils.data_generator.requests.get')
    @patch('Utils.data_generator.time.sleep', return_value=None)
    def test_fetch_all_issues_empty(self, mock_sleep, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = data_generator.fetch_all_issues()
        self.assertEqual(result, [])

    @patch('Utils.data_generator.requests.get')
    @patch('Utils.data_generator.time.sleep', return_value=None)
    def test_fetch_all_issues_with_error(self, mock_sleep, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response

        result = data_generator.fetch_all_issues()
        self.assertEqual(result, [])

    @patch('Utils.data_generator.requests.get')
    @patch('Utils.data_generator.fetch_issue_timeline')
    @patch('Utils.data_generator.time.sleep', return_value=None)
    def test_fetch_all_issues_success(self, mock_sleep, mock_fetch_timeline, mock_get):
        mock_issue = {
            "html_url": "http://example.com",
            "user": {"login": "creator"},
            "labels": [{"name": "bug"}],
            "state": "open",
            "assignees": [{"login": "dev1"}],
            "title": "Issue title",
            "body": "Issue body",
            "number": 100,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }

        mock_response_page = Mock()
        mock_response_page.status_code = 200
        mock_response_page.json.return_value = [mock_issue]

        mock_response_empty = Mock()
        mock_response_empty.status_code = 200
        mock_response_empty.json.return_value = []

        mock_get.side_effect = [mock_response_page, mock_response_empty]
        mock_fetch_timeline.return_value = ["dummy_event"]

        result = data_generator.fetch_all_issues()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['creator'], "creator")
        self.assertIn("dummy_event", result[0]['events'])




if __name__ == '__main__':
    unittest.main()
