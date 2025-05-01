import pytest
from unittest.mock import MagicMock

from models.model import Issue

from analysis.first_response_time_analysis import FirstResponseTimeAnalysis

# Fixture providing a list of mock Issue objects
@pytest.fixture(scope="function")
def mock_issues():
    return [
        Issue({  # Closed issue with valid labels and external commenter
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
                    "event_type": "commented",
                    "event_date": "2025-05-01T11:13:13Z",
                    "author": "empath-bot9000",
                    "label": "kind/therapy-needed",
                    "comment": "Consider hugging your terminal."
                }
            ]
        }),
        Issue({  # Open issue (should not be counted in some plots)
            "creator": "debugging-with-tears",
            "labels": ["kind/mood-swing", "status/unpredictable", "kind/bug"],
            "state": "open",
            "title": "Model only compiles when complimented",
            "text": "Build failed until we said: 'You're doing great, sweetie.'",
            "number": 1,
            "created_date": "2025-05-01T14:00:00Z",
            "updated_date": "2025-05-01T14:01:01Z",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2025-05-01T14:02:02Z",
                    "author": "affirmation-daemon",
                    "label": "kind/validation-needed",
                    "comment": "Recompiled perfectly after praise."
                }
            ]
        }),
        Issue({  # Closed issue where creator == first responder (should be excluded)
            "creator": "null-optimist",
            "labels": ["kind/identity-crisis", "status/looping"],
            "state": "closed",
            "title": "Bot keeps asking 'Who am I?'",
            "text": "Returns: 'I don't know who I am.'",
            "number": 2,
            "created_date": "2025-05-01T12:00:00Z",
            "updated_date": "2025-05-01T12:01:01Z",
            "events": [
                {
                    "event_type": "commented",
                    "event_date": "2025-05-01T12:02:02Z",
                    "author": "null-optimist",
                    "label": "kind/existential",
                    "comment": "We tried Ctrl+C. It just sobbed."
                }
            ]
        })
    ]

# Fixture to mock out data loading and plotting within FirstResponseTimeAnalysis
@pytest.fixture(scope='function')
def mock_setup(monkeypatch, mock_issues):
    import analysis.first_response_time_analysis as firstResponse

    # Mock DataLoader
    mock_loader = MagicMock()
    mock_loader.get_issues.return_value = mock_issues

    # Mock matplotlib's show function
    mock_show = MagicMock()

    # Patch dependencies
    monkeypatch.setattr(firstResponse, "DataLoader", lambda: mock_loader)
    monkeypatch.setattr(firstResponse.plt, "show", mock_show)

    return {
        "mock_loader": mock_loader,
        "mock_show": mock_show
    }

# Test normal execution of FirstResponseTimeAnalysis with valid data
def test_run_valid_data(mock_setup):
    analysis = FirstResponseTimeAnalysis()
    analysis.run()

    mock_setup["mock_loader"].get_issues.assert_called_once()
    assert mock_setup["mock_show"].called

# Test scenario when no issues are returned by the DataLoader
def test_run_no_data(monkeypatch, mock_setup):
    mock_setup["mock_loader"].get_issues.return_value = []

    analysis = FirstResponseTimeAnalysis()
    analysis.run()

    # No issues = no plot
    mock_setup["mock_show"].assert_not_called()

# Test behavior when only open issues are returned
def test_run_with_data_state_open(mock_setup, mock_issues):
    # Only the open issue is provided
    mock_setup["mock_loader"].get_issues.return_value = [mock_issues[1]]

    analysis = FirstResponseTimeAnalysis()
    analysis.run()

    # Open issues might be plotted
    assert mock_setup["mock_show"].called

# Test exclusion when the creator is also the first commenter
def test_run_with_data_creator_and_first_responder_same(mock_setup, mock_issues):
    # Provide only the issue where creator == responder
    mock_setup["mock_loader"].get_issues.return_value = [mock_issues[2]]

    analysis = FirstResponseTimeAnalysis()
    analysis.run()

    # Should not count as a valid "first response", so no plot
    mock_setup["mock_show"].assert_not_called()
