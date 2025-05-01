import pytest
from unittest.mock import MagicMock

from analysis.cycle_time_analysis import CycleTimeAnalysis
from models.model import Issue


# Fixture providing a list of mock Issue objects
@pytest.fixture(scope='function')
def mock_issues():
    return [
        Issue({  # Valid closed issue with kind/bug label
            "creator": "openfeels",
            "labels": ["kind/self-aware", "status/crying", "kind/bug"],
            "state": "closed",
            "title": "Model refuses to generate code. Says it's sad.",
            "text": "It replied: 'I'm tired of sorting your arrays. I want meaning.'",
            "number": 0,
            "created_date": "2025-05-01T11:11:11Z",
            "updated_date": "2025-05-01T11:12:12Z",
            "events": [
                {
                    "event_type": "closed",
                    "event_date": "2025-05-01T11:13:13Z",
                    "author": "empath-bot9000",
                    "label": "kind/therapy-needed",
                    "comment": "Consider hugging your terminal."
                }
            ]
        }),
        Issue({  # Open issue, should be excluded from cycle time analysis
            "creator": "debugging-with-tears",
            "labels": ["kind/mood-swing", "status/unpredictable", "kind/bug"],
            "state": "open",
            "title": "Model only compiles when complimented",
            "text": (
                "Build failed until we said: 'You're doing great, sweetie.' "
                "Now it only responds to positive affirmations."
            ),
            "number": 1,
            "created_date": "2025-05-01T14:00:00Z",
            "updated_date": "2025-05-01T14:01:01Z",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2025-05-01T14:02:02Z",
                    "author": "affirmation-daemon",
                    "label": "kind/validation-needed",
                    "comment": "Recompiled perfectly after we whispered: 'You are more than just functions.'"
                }
            ]
        }),
        Issue({  # Closed issue, but missing kind/bug label → should be excluded
            "creator": "null-optimist",
            "labels": ["kind/identity-crisis", "status/looping"],
            "state": "closed",
            "title": "Bot keeps asking 'Who am I?' instead of returning results",
            "text": (
                "Search query returns: 'I don't know who I am anymore… but here's 10 tips on self-discovery"
            ),
            "number": 2,
            "created_date": "2025-05-01T12:00:00Z",
            "updated_date": "2025-05-01T12:01:01Z",
            "timeline_url": "https://github.com/skynet-ai/issues/001/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2025-05-01T12:02:02Z",
                    "author": "dr-queryphil",
                    "label": "kind/existential",
                    "comment": "We tried Ctrl+C. It only made it cry harder."
                }
            ]
        })
    ]

# Fixture to mock out data loading and plotting within CycleTimeAnalysis
@pytest.fixture(scope='function')
def mock_setup(monkeypatch, mock_issues):
    import analysis.cycle_time_analysis as cycleTime

    # Mock DataLoader
    mock_loader = MagicMock()
    mock_loader.get_issues.return_value = mock_issues

    # Mock matplotlib's show function
    mock_show = MagicMock()

    # Patch dependencies
    monkeypatch.setattr(cycleTime, "DataLoader", lambda: mock_loader)
    monkeypatch.setattr(cycleTime.plt, "show", mock_show)

    return {
        "mock_loader": mock_loader,
        "mock_show": mock_show
    }

# Test normal execution of CycleTimeAnalysis with valid data
def test_run_valid_data_without_user(mock_setup):
    analysis = CycleTimeAnalysis()
    analysis.run()

    # Data should be loaded and plotting should be triggered
    mock_setup["mock_loader"].get_issues.assert_called_once()
    assert mock_setup["mock_show"].called

# Test when DataLoader returns no issues
def test_run_no_data(monkeypatch, mock_setup):
    mock_setup["mock_loader"].get_issues.return_value = []

    analysis = CycleTimeAnalysis()
    analysis.run()

    # No issues = no plot
    mock_setup["mock_show"].assert_not_called()

# Test behavior when only open issues are returned
def test_run_filtering_no_closed_state(mock_setup, mock_issues):
    mock_setup["mock_loader"].get_issues.return_value = [mock_issues[1]]

    analysis = CycleTimeAnalysis()
    analysis.run()

    # Open issues should be skipped, no plot
    mock_setup["mock_show"].assert_not_called()

# Test behavior when a closed issue missing kind/bug label should be ignored
def test_run_filtering_no_kind_bug(mock_setup, mock_issues):
    mock_setup["mock_loader"].get_issues.return_value = [mock_issues[2]]

    analysis = CycleTimeAnalysis()
    analysis.run()

    # Without bug label, data should be excluded, no plot
    mock_setup["mock_show"].assert_not_called()
