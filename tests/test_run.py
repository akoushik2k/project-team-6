import pytest
import sys
from unittest.mock import MagicMock
import os
import importlib

# Determine the path to the current test file
path_to_current_directory = os.path.dirname(os.path.abspath(__file__))

# Determine the root directory of the project (one level up)
path_to_project_root_directory = os.path.abspath(os.path.join(path_to_current_directory, '..'))

# Add the root directory to sys.path so imports from the project work
sys.path.append(path_to_project_root_directory)

# Pytest fixture that mocks all analysis classes in the `run` script
@pytest.fixture(scope='function')
def mock_setup(monkeypatch):
    # Replace actual analysis classes with MagicMock versions
    monkeypatch.setattr('analysis.example_analysis.ExampleAnalysis', MagicMock())
    monkeypatch.setattr('analysis.cycle_time_analysis.CycleTimeAnalysis', MagicMock())
    monkeypatch.setattr('analysis.first_response_time_analysis.FirstResponseTimeAnalysis', MagicMock())
    monkeypatch.setattr('analysis.top_twenty_analysis.TopTwentyAnalysis', MagicMock())

# TODO: Add tests for cases where feature or args are not provided

# Test parsing of command-line args with only the required --feature flag
def test_parse_args_with_required_flags(monkeypatch, mock_setup):
    mock_args = ['run.py', '--feature', '0']
    monkeypatch.setattr(sys, 'argv', mock_args)
    import run
    test_args = run.parse_args()
    assert test_args.feature == 0
    assert test_args.user is None
    assert test_args.label is None

# Test parsing of command-line args with --feature and optional --user and --label flags
def test_parse_args_with_optional_flags(monkeypatch, mock_setup):
    mock_args = ['run.py', '--feature', '1', '--user', 'mongoose', '--label', 'duel']
    monkeypatch.setattr(sys, 'argv', mock_args)
    import run
    test_args = run.parse_args()
    assert test_args.feature == 1
    assert test_args.user == 'mongoose'
    assert test_args.label == 'duel'

# Test if ExampleAnalysis is selected and run when --feature 0 is passed
def test_selects_example_analysis(monkeypatch, mock_setup):
    mock_args = ['run.py', '--feature', '0']
    monkeypatch.setattr(sys, 'argv', mock_args)
    import run
    importlib.reload(run)  # Ensure the mocked class is used fresh
    run.ExampleAnalysis.return_value.run.assert_called_once()

# Test if CycleTimeAnalysis is selected and run when --feature 1 is passed
def test_select_cycle_time_analysis(monkeypatch, mock_setup):
    mock_args = ['run.py', '--feature', '1']
    monkeypatch.setattr(sys, 'argv', mock_args)
    import run
    importlib.reload(run)
    run.CycleTimeAnalysis.return_value.run.assert_called_once()

# Test if TopTwentyAnalysis is selected and run when --feature 2 is passed
def test_select_top_twenty_analysis(monkeypatch, mock_setup):
    mock_args = ['run.py', '--feature', '2']
    monkeypatch.setattr(sys, 'argv', mock_args)
    import run
    importlib.reload(run)
    run.TopTwentyAnalysis.return_value.run.assert_called_once()

# Test if FirstResponseTimeAnalysis is selected and run when --feature 3 is passed
def test_select_first_response_time_analysis(monkeypatch, mock_setup):
    mock_args = ['run.py', '--feature', '3']
    monkeypatch.setattr(sys, 'argv', mock_args)
    import run
    importlib.reload(run)
    run.FirstResponseTimeAnalysis.return_value.run.assert_called_once()
