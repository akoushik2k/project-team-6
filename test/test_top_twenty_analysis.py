import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import json
from collections import Counter

# Add the parent directory to the path so Python can find the modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Now import the required modules
from analysis.top_twenty_analysis import TopTwentyAnalysis
from models.model import Issue, State, Event


class TestTopTwentyAnalysis(unittest.TestCase):
    """Test cases for TopTwentyAnalysis class"""
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create the analysis object
        self.analysis = TopTwentyAnalysis()
        
        # Create sample test data
        self.test_issues = self._create_test_issues()
        
        # Mock plt to avoid actual plotting
        self.plt_patcher = patch('analysis.top_twenty_analysis.plt')
        self.mock_plt = self.plt_patcher.start()
        
        # Mock mplcursors
        self.mplcursors_patcher = patch('analysis.top_twenty_analysis.mplcursors')
        self.mock_mplcursors = self.mplcursors_patcher.start()
        self.mock_cursor = MagicMock()
        self.mock_mplcursors.cursor.return_value = self.mock_cursor
        
        # Mock mplcyberpunk
        self.mplcyberpunk_patcher = patch('analysis.top_twenty_analysis.mplcyberpunk')
        self.mock_mplcyberpunk = self.mplcyberpunk_patcher.start()
        
        # Mock DataLoader
        self.data_loader_patcher = patch('analysis.top_twenty_analysis.DataLoader')
        self.mock_data_loader_class = self.data_loader_patcher.start()
        self.mock_data_loader = MagicMock()
        self.mock_data_loader_class.return_value = self.mock_data_loader
        self.mock_data_loader.get_issues.return_value = self.test_issues
        
        # Mock pd.DataFrame and related functions
        self.dataframe_patcher = patch('analysis.top_twenty_analysis.pd.DataFrame')
        self.mock_dataframe = self.dataframe_patcher.start()
        
        # Create sample DataFrames for different parts of the analysis
        self.contrib_df = pd.DataFrame({
            'contributor': ['user1', 'user2', 'user3'],
            'num_issues': [3, 2, 1]
        })
        
        self.creator_df = pd.DataFrame({
            'creator': ['user1', 'user4', 'user3'],
            'num_created': [2, 1, 1]
        })
        
        self.closers_df = pd.DataFrame({
            'author': ['user2', 'user1', 'user3'],
            'closes': [2, 1, 1]
        })
        
        # Set up the side effect for DataFrame creation
        self.mock_dataframe.return_value = self.contrib_df
        
        # Mock pd.DataFrame.from_records for the closers analysis
        self.from_records_patcher = patch('analysis.top_twenty_analysis.pd.DataFrame.from_records')
        self.mock_from_records = self.from_records_patcher.start()
        self.mock_from_records.return_value = self.closers_df
        
        # Mock collections.Counter
        self.counter_patcher = patch('analysis.top_twenty_analysis.Counter')
        self.mock_counter = self.counter_patcher.start()
        self.mock_counter.return_value = Counter({'user2': 2, 'user1': 1, 'user3': 1})

    def tearDown(self):
        self.plt_patcher.stop()
        self.mplcursors_patcher.stop()
        self.mplcyberpunk_patcher.stop()
        self.data_loader_patcher.stop()
        self.dataframe_patcher.stop()
        self.from_records_patcher.stop()
        self.counter_patcher.stop()

    def _create_test_issues(self):
        # Issue 1: Multiple contributors
        issue1_json = {
            "url": "https://github.com/python-poetry/poetry/issues/1",
            "creator": "user1",
            "labels": ["bug"],
            "state": "closed",
            "assignees": ["user2", "user3"],
            "title": "Issue with multiple contributors",
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
                    "event_type": "closed",
                    "event_date": "2022-01-10T00:00:00Z",
                    "author": "user3"
                }
            ]
        }
        
        # Issue 2: Bot contributor (should be filtered)
        issue2_json = {
            "url": "https://github.com/python-poetry/poetry/issues/2",
            "creator": "dependabot[bot]",
            "labels": ["enhancement"],
            "state": "closed",
            "assignees": [],
            "title": "Issue with bot",
            "text": "Test issue 2",
            "number": 2,
            "created_date": "2022-02-01T00:00:00Z",
            "updated_date": "2022-02-20T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/2/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2022-02-05T00:00:00Z",
                    "author": "user1"
                },
                {
                    "event_type": "closed",
                    "event_date": "2022-02-20T00:00:00Z",
                    "author": "user1"
                }
            ]
        }
        
        # Issue 3: Regular contributors
        issue3_json = {
            "url": "https://github.com/python-poetry/poetry/issues/3",
            "creator": "user4",
            "labels": ["question"],
            "state": "open",
            "assignees": ["user1"],
            "title": "Another issue",
            "text": "Test issue 3",
            "number": 3,
            "created_date": "2022-03-01T00:00:00Z",
            "updated_date": "2022-03-10T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/3/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2022-03-02T00:00:00Z",
                    "author": "user1"
                },
                {
                    "event_type": "commented",
                    "event_date": "2022-03-05T00:00:00Z",
                    "author": "user5"
                }
            ]
        }
        
        # Issue 4: Empty events (edge case)
        issue4_json = {
            "url": "https://github.com/python-poetry/poetry/issues/4",
            "creator": "user1",
            "labels": ["bug"],
            "state": "closed",
            "assignees": [],
            "title": "Issue with no events",
            "text": "Test issue 4",
            "number": 4,
            "created_date": "2022-04-01T00:00:00Z",
            "updated_date": "2022-04-15T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/4/timeline",
            "events": []
        }
        
        # Issue 5: Null creator (edge case)
        issue5_json = {
            "url": "https://github.com/python-poetry/poetry/issues/5",
            "creator": None,
            "labels": ["bug"],
            "state": "open",
            "assignees": ["user2"],
            "title": "Issue with null creator",
            "text": "Test issue 5",
            "number": 5,
            "created_date": "2022-05-01T00:00:00Z",
            "updated_date": "2022-05-05T00:00:00Z",
            "timeline_url": "https://api.github.com/repos/python-poetry/poetry/issues/5/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2022-05-03T00:00:00Z",
                    "author": "user2"
                }
            ]
        }
        
        return [
            Issue(issue1_json),
            Issue(issue2_json),
            Issue(issue3_json),
            Issue(issue4_json),
            Issue(issue5_json)
        ]

    def test_constants(self):
        """Test class constants"""
        self.assertEqual(self.analysis.BOT_REGEX, r"\[bot\]")
        self.assertEqual(self.analysis.TOP_N, 20)

    @patch('analysis.top_twenty_analysis.print')
    def test_run_with_data(self, mock_print):
        """Test run method with valid data"""
        # Setup mocks for DataFrame handling
        self.mock_dataframe.side_effect = [self.contrib_df, self.creator_df]
        self.contrib_df.empty = False
        self.contrib_df.iloc = MagicMock()
        self.contrib_df.iloc.__getitem__.return_value = {'contributor': 'user1', 'num_issues': 3}
        self.contrib_df.head.return_value = self.contrib_df
        
        self.creator_df.empty = False
        self.creator_df.iloc = MagicMock()
        self.creator_df.iloc.__getitem__.return_value = {'creator': 'user1', 'num_created': 2}
        self.creator_df.head.return_value = self.creator_df
        
        self.closers_df.head.return_value = self.closers_df
        
        self.analysis.run()
        
        self.mock_data_loader.get_issues.assert_called_once()
        
        self.mock_plt.style.use.assert_called_once_with("cyberpunk")
        
        self.mock_plt.show.assert_called_once()
        
        # Verify print was called with expected values
        mock_print.assert_any_call(f"Real contributors: {len(self.contrib_df)}")

    @patch('analysis.top_twenty_analysis.print')
    def test_run_with_empty_data(self, mock_print):
        """Test run method with empty contributor data"""
        # Setup empty DataFrame
        empty_df = MagicMock()
        empty_df.empty = True
        self.mock_dataframe.return_value = empty_df
        
        self.analysis.run()
        
        # Verify early return message
        mock_print.assert_any_call("No real contributors (all bots).")
        
        # Verify plt.show was not called
        self.mock_plt.show.assert_not_called()

    def test_contributor_mapping(self):
        """Test that contributors are correctly mapped to issues"""
        # Set up to capture the contributor map
        contrib_issues = {}
        
        # Mock pd.DataFrame to capture the contributor map
        def capture_contrib_issues(*args, **kwargs):
            nonlocal contrib_issues
            if args and isinstance(args[0], list) and len(args[0]) > 0:
                if 'contributor' in args[0][0] and 'num_issues' in args[0][0]:
                    for item in args[0]:
                        contrib_issues[item['contributor']] = item['num_issues']
            return self.contrib_df
        
        self.mock_dataframe.side_effect = capture_contrib_issues
        
        with patch('analysis.top_twenty_analysis.print'):
            self.analysis.run()
        
        # Verify that the contributor mapping contains expected contributors
        self.assertTrue('user1' in contrib_issues or len(contrib_issues) > 0)

    @patch('analysis.top_twenty_analysis.print')
    def test_closers_analysis(self, mock_print):
        """Test the closers analysis logic"""
        # Mock DataFrame.from_records to return our test data
        self.mock_from_records.return_value = self.closers_df
        self.closers_df.sort_values = MagicMock(return_value=self.closers_df)
        self.closers_df.reset_index = MagicMock(return_value=self.closers_df)
        self.closers_df.head = MagicMock(return_value=self.closers_df)
        
        self.analysis.run()
        
        self.mock_counter.assert_called()
        
        # Verify DataFrame.from_records was called with expected columns
        args, kwargs = self.mock_from_records.call_args
        self.assertEqual(kwargs.get('columns'), ["author", "closes"])
        
        # Verify plotting function was called for closers
        self.mock_plt.subplots.assert_called()

    def test_plot_barh_method(self):
        """Test the _plot_barh helper method"""
        # Create a test DataFrame
        test_df = pd.DataFrame({
            'contributor': ['user1', 'user2', 'user3'],
            'num_issues': [10, 8, 6]
        })
        
        # Mock the subplots return value
        fig_mock = MagicMock()
        ax_mock = MagicMock()
        self.mock_plt.subplots.return_value = (fig_mock, ax_mock)
        
        # Call the method directly
        self.analysis._plot_barh(
            test_df,
            value_col="num_issues",
            label_col="contributor",
            title="Test Plot",
            xlabel="Issues",
            color="C0"
        )
        
        # Verify matplotlib calls
        self.mock_plt.subplots.assert_called_once()
        
        # Verify various ax method calls
        ax_mock.barh.assert_called_once()
        ax_mock.set_title.assert_called_once_with("Test Plot")
        ax_mock.set_xlabel.assert_called_once_with("Issues")
        ax_mock.set_ylabel.assert_called_once_with("Contributor")
        ax_mock.invert_yaxis.assert_called_once()
        
        # Verify cyberpunk effects
        self.mock_mplcyberpunk.add_glow_effects.assert_called()
        
        # Verify cursor setup
        self.mock_mplcursors.cursor.assert_called()

    def test_bot_filtering(self):
        """Test that bots are correctly filtered out"""
        # Set up to capture the DataFrame query
        query_args = []
        
        # Create a mock DataFrame with a query method to capture arguments
        mock_df = MagicMock()
        mock_df.query = MagicMock(return_value=mock_df)
        
        def capture_query(*args, **kwargs):
            nonlocal query_args
            if args and isinstance(args[0], str) and 'bot' in args[0].lower():
                query_args.append(args[0])
            return mock_df
        
        mock_df.query.side_effect = capture_query
        
        # Set up the DataFrame mock to return our mock
        self.mock_dataframe.return_value = mock_df
        
        with patch('analysis.top_twenty_analysis.print'):
            self.analysis.run()
        
        # Verify the bot filtering query was called
        self.assertTrue(any("bot" in query.lower() for query in query_args))

    def test_cursor_callback(self):
        """Test that the cursor callback is set up correctly"""
        # Setup mocks
        mock_bars = MagicMock()
        self.mock_mplcursors.cursor.return_value = self.mock_cursor
        
        # Create a test DataFrame for the _plot_barh method
        test_df = pd.DataFrame({
            'contributor': ['user1', 'user2'],
            'num_issues': [10, 8]
        })
        
        # Mock the subplots return value
        fig_mock = MagicMock()
        ax_mock = MagicMock()
        ax_mock.barh.return_value = mock_bars
        self.mock_plt.subplots.return_value = (fig_mock, ax_mock)
        
        # Call the method
        self.analysis._plot_barh(
            test_df,
            value_col="num_issues",
            label_col="contributor",
            title="Test Plot",
            xlabel="Issues",
            color="C0"
        )
        
        # Verify cursor was set up with the bars
        self.mock_mplcursors.cursor.assert_called_with(mock_bars, hover=True)
        
        # Verify connect was called
        self.mock_cursor.connect.assert_called_with('add')
        
        # Test the callback function directly if possible
        callback_func = self.mock_cursor.connect.call_args[1].get('callback')
        if not callback_func:
            # If we can't get the callback directly, check it was connected correctly
            self.assertEqual(self.mock_cursor.connect.call_args[0][0], 'add')

    def test_edge_cases(self):
        """Test various edge cases"""
        # Test with None values in issue fields
        edge_case_issue_json = {
            "url": "https://github.com/python-poetry/poetry/issues/6",
            "creator": None,
            "labels": None,
            "state": None,
            "assignees": None,
            "title": None,
            "text": None,
            "number": None,
            "created_date": None,
            "updated_date": None,
            "timeline_url": None,
            "events": [
                {
                    "event_type": None,
                    "event_date": None,
                    "author": None
                }
            ]
        }
        
        edge_case_issue = Issue(edge_case_issue_json)
        
        # Add the edge case issue to our test data
        self.test_issues.append(edge_case_issue)
        
        with patch('analysis.top_twenty_analysis.print'):
            self.analysis.run()
        
        # Verify the function executes without errors
        self.mock_data_loader.get_issues.assert_called_once()
        
        # The edge case should not break the analysis
        self.mock_plt.show.assert_called_once()