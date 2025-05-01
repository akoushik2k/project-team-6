import pytest
from unittest.mock import MagicMock

from analysis.top_twenty_analysis import TopTwentyAnalysis
from models.model import Issue, State

# Fixture providing a list of mock issues for use in tests
@pytest.fixture(scope="function")
def mock_issues():
    return [
        Issue({  # Closed issue, valid data
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
        Issue({  # Open issue, should be ignored in closer analysis
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
        Issue({  # Closed issue but not labeled as a bug and creator == commenter
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

# Fixture to mock out data loading and plotting within TopTwentyAnalysis
@pytest.fixture(scope='function')
def mock_setup(monkeypatch, mock_issues):
    import analysis.top_twenty_analysis as topAnalysis

    # Mock DataLoader
    mock_loader = MagicMock()
    mock_loader.get_issues.return_value = mock_issues

    # Mock matplotlib's show function
    mock_show = MagicMock()

    # Patch dependencies
    monkeypatch.setattr(topAnalysis, "DataLoader", lambda: mock_loader)
    monkeypatch.setattr(topAnalysis.plt, "show", mock_show)

    return {
        "mock_loader": mock_loader,
        "mock_show": mock_show
    }

# Test normal execution of TopTwentyAnalysis with valid data
def test_run_valid_data(mock_setup):
    analysis = TopTwentyAnalysis()
    analysis.run()

    # Ensure data was loaded and a plot was attempted
    mock_setup["mock_loader"].get_issues.assert_called_once()
    assert mock_setup["mock_show"].called

# Test scenario when no issues are returned by the DataLoader
def test_run_no_data(mock_setup):
    mock_setup["mock_loader"].get_issues.return_value = []

    analysis = TopTwentyAnalysis()
    analysis.run()

    # No data to plot means no call to plt.show()
    mock_setup["mock_show"].assert_not_called()

# Test behavior when all users involved are bots
def test_run_all_bots(mock_setup, mock_issues):
    for issue in mock_issues:
        issue.creator = "[bot]"
        issue.assignees = ["bot[bot]"]
        for event in issue.events:
            event.author = "[bot]"

    mock_setup["mock_loader"].get_issues.return_value = mock_issues

    analysis = TopTwentyAnalysis()
    analysis.run()

    # All data filtered out, no plot
    mock_setup["mock_show"].assert_not_called()

# Test behavior when only open issues are returned (no closed contributors)
def test_run_only_open_issues(mock_setup, mock_issues):
    open_issues = [i for i in mock_issues if i.state == State.open]

    mock_setup["mock_loader"].get_issues.return_value = open_issues

    analysis = TopTwentyAnalysis()
    analysis.run()

    # Might still generate plots (contributor plot)
    assert mock_setup["mock_show"].called
