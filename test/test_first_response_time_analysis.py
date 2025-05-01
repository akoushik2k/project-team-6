import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import json

# Add the parent directory to the path so Python can find the modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Now import the required modules
from analysis.first_response_time_analysis import FirstResponseTimeAnalysis
from models.model import Issue, State, Event


class TestFirstResponseTimeAnalysis(unittest.TestCase):
    """Test cases for FirstResponseTimeAnalysis class"""
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock the config.get_parameter method
        self.config_patcher = patch('analysis.first_response_time_analysis.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.get_parameter.return_value = "test_user"
        
        # Create the analysis object
        self.analysis = FirstResponseTimeAnalysis()
        
        # Create sample test data
        self.test_issues = self._create_test_issues()
        
        # Mock plt to avoid actual plotting
        self.plt_patcher = patch('analysis.first_response_time_analysis.plt')
        self.mock_plt = self.plt_patcher.start()
        
        # Set up mock for plt.hist to return the expected tuple
        self.mock_plt.hist.return_value = (
            np.array([1, 2]),  # counts
            np.array([0, 5, 10]),  # bin_edges
            MagicMock()  # patches
        )
        
        # Mock mplcursors
        self.mplcursors_patcher = patch('analysis.first_response_time_analysis.mplcursors')
        self.mock_mplcursors = self.mplcursors_patcher.start()
        self.mock_cursor = MagicMock()
        self.mock_mplcursors.cursor.return_value = self.mock_cursor
        
        # Mock mplcyberpunk
        self.mplcyberpunk_patcher = patch('analysis.first_response_time_analysis.mplcyberpunk')
        self.mock_mplcyberpunk = self.mplcyberpunk_patcher.start()
        
        # Mock DataLoader
        self.data_loader_patcher = patch('analysis.first_response_time_analysis.DataLoader')
        self.mock_data_loader_class = self.data_loader_patcher.start()
        self.mock_data_loader = MagicMock()
        self.mock_data_loader_class.return_value = self.mock_data_loader
        self.mock_data_loader.get_issues.return_value = self.test_issues
        
        # Create test data for DataFrames
        self.response_times = [
            {
                "issue_number": 1,
                "title": "Issue with comments",
                "first_response_days": 2.0,
                "created_date": datetime(2022, 1, 1),
                "responder": "user2"
            },
            {
                "issue_number": 2,
                "title": "Issue with various events",
                "first_response_days": 2.0,
                "created_date": datetime(2022, 2, 1),
                "responder": "user2"
            }
        ]
        
        self.label_groups = [
            {
                "label": "bug",
                "first_response_days": 2.0
            },
            {
                "label": "documentation",
                "first_response_days": 2.0
            },
            {
                "label": "enhancement",
                "first_response_days": 2.0
            }
        ]
        
        # Create DataFrames
        self.df = pd.DataFrame(self.response_times)
        self.label_df = pd.DataFrame(self.label_groups)
        
        # Mock pd.DataFrame to return our test DataFrames
        self.dataframe_patcher = patch('analysis.first_response_time_analysis.pd.DataFrame')
        self.mock_dataframe = self.dataframe_patcher.start()
        self.mock_dataframe.side_effect = [self.df, self.label_df]

    def tearDown(self):
        self.config_patcher.stop()
        self.plt_patcher.stop()
        self.mplcursors_patcher.stop()
        self.mplcyberpunk_patcher.stop()
        self.data_loader_patcher.stop()
        self.dataframe_patcher.stop()

    def _create_test_issues(self):
        # Issue 1: Has comments from different users
        issue1_json = {
            "url": "https://github.com/python-poetry/poetry/issues/1",
            "creator": "user1",
            "labels": ["bug", "documentation"],
            "state": "open",
            "assignees": [],
            "title": "Issue with comments",
            "text": "Test issue 1",
            "number": 1,
            "created_date": "2022-01-01T00:00:00Z",
            "updated_date": "2022-01-10T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/1/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2022-01-03T00:00:00Z",
                    "author": "user2"
                },
                {
                    "event_type": "commented",
                    "event_date": "2022-01-05T00:00:00Z",
                    "author": "user3"
                }
            ]
        }
        
        # Issue 2: Has reference, assigned, and mentioned events
        issue2_json = {
            "url": "https://github.com/python-poetry/poetry/issues/2",
            "creator": "user1",
            "labels": ["enhancement"],
            "state": "closed",
            "assignees": [],
            "title": "Issue with various events",
            "text": "Test issue 2",
            "number": 2,
            "created_date": "2022-02-01T00:00:00Z",
            "updated_date": "2022-02-20T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/2/timeline",
            "events": [
                {
                    "event_type": "referenced",
                    "event_date": "2022-02-05T00:00:00Z",
                    "author": "user4"
                },
                {
                    "event_type": "assigned",
                    "event_date": "2022-02-03T00:00:00Z",
                    "author": "user2"
                },
                {
                    "event_type": "mentioned",
                    "event_date": "2022-02-10T00:00:00Z",
                    "author": "user5"
                }
            ]
        }
        
        # Issue 3: Comments only from the creator (should be filtered out)
        issue3_json = {
            "url": "https://github.com/python-poetry/poetry/issues/3",
            "creator": "user6",
            "labels": ["question"],
            "state": "open",
            "assignees": [],
            "title": "Issue with creator comments",
            "text": "Test issue 3",
            "number": 3,
            "created_date": "2022-03-01T00:00:00Z",
            "updated_date": "2022-03-10T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/3/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2022-03-02T00:00:00Z",
                    "author": "user6"  # Same as creator
                },
                {
                    "event_type": "commented",
                    "event_date": "2022-03-05T00:00:00Z",
                    "author": "user6"  # Same as creator
                }
            ]
        }
        
        # Issue 4: No created_date (edge case)
        issue4_json = {
            "url": "https://github.com/python-poetry/poetry/issues/4",
            "creator": "user7",
            "labels": ["bug"],
            "state": "closed",
            "assignees": [],
            "title": "Issue with missing created date",
            "text": "Test issue 4",
            "number": 4,
            "created_date": None,  # Missing created_date
            "updated_date": "2022-04-15T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/4/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2022-04-10T00:00:00Z",
                    "author": "user8"
                }
            ]
        }
        
        # Issue 5: No events (edge case)
        issue5_json = {
            "url": "https://github.com/python-poetry/poetry/issues/5",
            "creator": "user9",
            "labels": ["bug"],
            "state": "open",
            "assignees": [],
            "title": "Issue with no events",
            "text": "Test issue 5",
            "number": 5,
            "created_date": "2022-05-01T00:00:00Z",
            "updated_date": "2022-05-05T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/5/timeline",
            "events": []
        }
        
        # Issue 6: Events without dates (edge case)
        issue6_json = {
            "url": "https://github.com/python-poetry/poetry/issues/6",
            "creator": "user10",
            "labels": ["bug"],
            "state": "open",
            "assignees": [],
            "title": "Issue with events missing dates",
            "text": "Test issue 6",
            "number": 6,
            "created_date": "2022-06-01T00:00:00Z",
            "updated_date": "2022-06-10T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/6/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": None,  # Missing date
                    "author": "user11"
                }
            ]
        }
        
        return [
            Issue(issue1_json),
            Issue(issue2_json),
            Issue(issue3_json),
            Issue(issue4_json),
            Issue(issue5_json),
            Issue(issue6_json)
        ]

    def test_init(self):
        """Test the constructor"""
        self.assertEqual(self.analysis.USER, "test_user")
        self.mock_config.get_parameter.assert_called_once_with("user")

    def test_run_with_data(self):
        """Test run method with valid data"""
        # Call the run method
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify DataLoader was called
        self.mock_data_loader.get_issues.assert_called_once()
        
        # Verify plotting calls
        self.mock_plt.style.use.assert_called_once_with("cyberpunk")
        self.mock_plt.figure.assert_called()
        self.mock_plt.title.assert_called()
        self.mock_plt.xlabel.assert_called()
        self.mock_plt.ylabel.assert_called()
        self.mock_plt.show.assert_called_once()
        
        # Verify cyberpunk effects added
        self.mock_mplcyberpunk.add_glow_effects.assert_called()

    def test_run_with_empty_data(self):
        """Test run method with empty data"""
        # Set up an empty DataFrame
        empty_df = pd.DataFrame([])
        self.mock_dataframe.return_value = empty_df
        
        # Call the run method
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify early return without plotting
        self.mock_plt.show.assert_not_called()

    def test_filtering_logic(self):
        """Test issue filtering logic for first response times"""
        # Capture the response_times data
        response_times_capture = []
        
        def capture_response_times(data):
            nonlocal response_times_capture
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'first_response_days' in data[0]:
                response_times_capture = data
                return self.df
            return self.label_df
        
        self.mock_dataframe.side_effect = capture_response_times
        
        # Call the run method
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify that at least some events were found
        self.assertTrue(len(response_times_capture) > 0)
        
        # Check that creator comments were filtered out
        issue3_data = next((item for item in response_times_capture if item['issue_number'] == 3), None)
        self.assertIsNone(issue3_data, "Issue 3 should be filtered out as all comments are from creator")
        
        # Check that issue with no created_date was filtered out
        issue4_data = next((item for item in response_times_capture if item['issue_number'] == 4), None)
        self.assertIsNone(issue4_data, "Issue 4 should be filtered out as it has no created_date")
        
        # Check that issue with no events was filtered out
        issue5_data = next((item for item in response_times_capture if item['issue_number'] == 5), None)
        self.assertIsNone(issue5_data, "Issue 5 should be filtered out as it has no events")

    @patch('analysis.first_response_time_analysis.print')
    def test_print_stats(self, mock_print):
        """Test the print statement for stats"""
        self.analysis.run()
        
        # Check that print was called with the average and median stats
        avg_response = self.df["first_response_days"].mean()
        median_response = self.df["first_response_days"].median()
        mock_print.assert_any_call(f"\nAverage first response time: {avg_response:.2f} days")
        mock_print.assert_any_call(f"Median first response time:  {median_response:.2f} days")
        
        # Verify print was called
        self.assertTrue(mock_print.call_count >= 2)

    def test_histogram_creation(self):
        """Test that the histogram is created with correct parameters"""        
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify histogram creation
        self.mock_plt.hist.assert_called()
        # Check histogram params
        args, kwargs = self.mock_plt.hist.call_args
        self.assertEqual(kwargs.get('edgecolor'), 'white')
        self.assertEqual(kwargs.get('bins'), 30)

    def test_label_stats_plot(self):
        """Test that label stats plot is created"""
        # Need to make sure label_df is not empty
        self.label_df = pd.DataFrame(self.label_groups)
        
        # Need to fix the side effect for when call groupby
        label_stats_mock = MagicMock()
        self.label_df.groupby = MagicMock(return_value=label_stats_mock)
        label_stats_mock.__getitem__ = MagicMock(return_value=label_stats_mock)
        label_stats_mock.mean = MagicMock(return_value=label_stats_mock)
        label_stats_mock.sort_values = MagicMock(return_value=pd.Series({
            'bug': 2.0, 
            'documentation': 2.5, 
            'enhancement': 3.0
        }))
        
        # Mock plot function to return a MagicMock
        plot_mock = MagicMock()
        label_stats_mock.plot = MagicMock(return_value=plot_mock)
        
        # Run the analysis with the mocked dataframe operations
        with patch('analysis.first_response_time_analysis.print'):
            with patch.object(pd.DataFrame, 'empty', new_callable=MagicMock(return_value=False)):
                self.analysis.run()
        
        # Verify that figure was created multiple times (for different plots)
        self.assertTrue(self.mock_plt.figure.call_count >= 2)
        self.mock_plt.title.assert_any_call("Average First Response Time by Label")
        self.mock_plt.xlabel.assert_any_call("Avg Response Time (days)")
        self.mock_plt.ylabel.assert_any_call("Label")

    def test_time_trend_plot(self):
        """Test that the time trend plot is created"""
        # Need to patch the dt properties and methods
        date_mock = MagicMock()
        self.df["created_date"] = MagicMock()
        self.df["created_date"].dt = date_mock
        date_mock.to_period = MagicMock(return_value=date_mock)
        date_mock.astype = MagicMock(return_value=['2022-01', '2022-02'])
        
        # Mock the monthly_avg variable
        monthly_avg = pd.Series({
            '2022-01': 2.0,
            '2022-02': 3.0
        })
        
        # Run the analysis with patched monthly_avg
        with patch('analysis.first_response_time_analysis.print'):
            with patch.object(pd.DataFrame, 'groupby') as mock_groupby:
                mock_group = MagicMock()
                mock_groupby.return_value = mock_group
                mock_group.__getitem__ = MagicMock(return_value=mock_group)
                mock_group.mean = MagicMock(return_value=monthly_avg)
                
                # Mock the plot method
                monthly_avg.plot = MagicMock()
                
                # Make sure check for empty doesn't return True
                monthly_avg.empty = False
                
                self.analysis.run()
        
        # Verify that multiple figures were created
        self.assertTrue(self.mock_plt.figure.call_count >= 3)
        self.mock_plt.title.assert_any_call("Average First Response Time Over a Period")
        self.mock_plt.xlabel.assert_any_call("Month")
        self.mock_plt.ylabel.assert_any_call("Avg Response Time (days)")

    def test_cursor_callback(self):
        """Test the cursor callback function is properly set up"""
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify cursor was set up
        self.mock_mplcursors.cursor.assert_called()
        self.mock_cursor.connect.assert_called_with('add')
        
        # Test the callback function directly if possible
        # Get the decorator and its argument
        decorator_call = self.mock_cursor.connect.call_args
        decorator_name = decorator_call[0][0]  # 'add'
        
        # Assert the decorator name is correct
        self.assertEqual(decorator_name, 'add')

    @patch('analysis.first_response_time_analysis.pd.DataFrame.sort_values')
    @patch('analysis.first_response_time_analysis.print')
    def test_slowest_responses(self, mock_print, mock_sort_values):
        """Test that top 5 slowest responses are printed"""
        # Mock the sorted dataframe
        mock_sorted_df = MagicMock()
        mock_sort_values.return_value = mock_sorted_df
        
        # Create a sample DataFrame for the head result
        slowest_responses = pd.DataFrame({
            'issue_number': [10, 20],
            'first_response_days': [30.5, 25.2],
            'responder': ['user8', 'user9']
        })
        mock_sorted_df.head.return_value = slowest_responses
        
        self.analysis.run()
        
        # Verify print calls for slowest responses
        mock_print.assert_any_call("Top 5 Slowest First Responses:")
        
        # Verify sort_values was called with the right parameters
        mock_sort_values.assert_called_with("first_response_days", ascending=False)
        
        # Verify head was called with the right parameters
        mock_sorted_df.head.assert_called_with(5)
        
        # Check that print was called for each slow response
        for _, row in slowest_responses.iterrows():
            mock_print.assert_any_call(
                f"Issue #{row['issue_number']} — {row['first_response_days']:.2f} days (by {row['responder']})"
            )

    def test_response_time_calculation(self):
        """Test that response times are calculated correctly"""
        # Capture the response_times data
        response_times_capture = []
        
        def capture_response_times(data):
            nonlocal response_times_capture
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'first_response_days' in data[0]:
                response_times_capture = data
                return self.df
            return self.label_df
        
        self.mock_dataframe.side_effect = capture_response_times
        
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify captured some response times
        self.assertTrue(len(response_times_capture) > 0)
        
        # Check response time calculation for Issue 1
        issue1_data = next((item for item in response_times_capture if item['issue_number'] == 1), None)
        self.assertIsNotNone(issue1_data)
        
        # For Issue 1: First event is a comment by user2 on 2022-01-03, created on 2022-01-01 = 2 days
        issue1_expected_days = 2.0  # (2022-01-03 - 2022-01-01).days = 2
        
        # The actual computation might differ slightly due to floating point,
        # so check that it's close rather than exactly equal
        self.assertAlmostEqual(issue1_data['first_response_days'], issue1_expected_days, delta=0.1)
        
        # Check response time calculation for Issue 2
        issue2_data = next((item for item in response_times_capture if item['issue_number'] == 2), None)
        self.assertIsNotNone(issue2_data)
        
        # For Issue 2: First relevant event is assigned by user2 on 2022-02-03, created on 2022-02-01 = 2 days
        issue2_expected_days = 2.0  # (2022-02-03 - 2022-02-01).days = 2
        
        # Check that it's close to the expected value
        self.assertAlmostEqual(issue2_data['first_response_days'], issue2_expected_days, delta=0.1)

    def test_edge_cases(self):
        """Test edge cases in the response time analysis"""
        # Test with missing created_date
        # Issue 4 has no created_date but has comments
        # The analysis should skip it
        
        # Test with no events
        # Issue 5 has no events
        # The analysis should skip it
        
        # Test with events missing dates
        # Issue 6 has an event with no date
        # The analysis should skip this event
        
        # Capture the response_times to verify our expectations
        response_times_capture = []
        
        def capture_response_times(data):
            nonlocal response_times_capture
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'first_response_days' in data[0]:
                response_times_capture = data
                return self.df
            return self.label_df
        
        self.mock_dataframe.side_effect = capture_response_times
        
        with patch('analysis.first_response_time_analysis.print'):
            self.analysis.run()
        
        # Verify don't have entries for these edge cases
        issue4_data = next((item for item in response_times_capture if item['issue_number'] == 4), None)
        self.assertIsNone(issue4_data, "Issue 4 with missing created_date should be skipped")
        
        issue5_data = next((item for item in response_times_capture if item['issue_number'] == 5), None)
        self.assertIsNone(issue5_data, "Issue 5 with no events should be skipped")
        
        issue6_data = next((item for item in response_times_capture if item['issue_number'] == 6), None)
        self.assertIsNone(issue6_data, "Issue 6 with event missing date should be skipped")