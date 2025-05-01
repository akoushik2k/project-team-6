import pytest
from unittest.mock import MagicMock
from models.model import Issue


# Fixture providing a list of mock Issue objects
@pytest.fixture(scope='function')
def mock_issues():
    return [
        Issue({  # Closed issue with valid structure and external closing author
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
        Issue({  # Open issue (should still be accepted by loader)
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
        Issue({  # Closed issue with no `kind/bug` label; valid timeline URL
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

# Fixture to mock out data loading, plotting, and config.get_parameter within ExampleAnalysis
@pytest.fixture(scope='function')
def mock_setup(monkeypatch, mock_issues):
    import analysis.example_analysis as example

    # Mock DataLoader
    mock_loader = MagicMock()
    mock_loader.get_issues.return_value = mock_issues

    # Mock matplotlib's show function
    mock_show = MagicMock()

    # Patch dependencies
    monkeypatch.setattr(example, "DataLoader", lambda: mock_loader)
    monkeypatch.setattr(example.plt, "show", mock_show)
    monkeypatch.setattr(example.config, "get_parameter", lambda key: None)

    return {
        "mod": example,
        "mock_loader": mock_loader,
        "mock_show": mock_show
    }


# Test run() when no specific user filter is set
def test_run_no_user(mock_setup):
    analysis = mock_setup["mod"].ExampleAnalysis()
    analysis.run()

    # Data is loaded and plot is shown
    mock_setup["mock_loader"].get_issues.assert_called_once()
    assert mock_setup["mock_show"].called

# Test run() when a specific user is passed via config.get_parameter
def test_run_with_user(monkeypatch, mock_setup):
    # Simulate user filter by monkeypatching config.get_parameter
    monkeypatch.setattr(mock_setup["mod"].config, "get_parameter", lambda key: "empath-bot9000")

    analysis = mock_setup["mod"].ExampleAnalysis()
    analysis.run()

    # Should still fetch and plot data for matching user
    mock_setup["mock_loader"].get_issues.assert_called_once()
    assert mock_setup["mock_show"].called

# Test run() when returned issues have no usable event data (e.g. empty events)
def test_run_no_data(monkeypatch, mock_setup):
    dummy_issue = Issue({  # Edge case: no events to plot
        "creator": "nobody",
        "labels": [],
        "state": "open",
        "title": "no events",
        "text": "noop",
        "number": 9,
        "created_date": "2025-05-01T00:00:00Z",
        "updated_date": "2025-05-01T00:01:00Z",
        "events": []
    })

    # Override DataLoader to return one empty issue
    mock_setup["mock_loader"].get_issues.return_value = [dummy_issue]
    monkeypatch.setattr(mock_setup["mod"].config, "get_parameter", lambda key: "ghost-user")

    analysis = mock_setup["mod"].ExampleAnalysis()
    analysis.run()

    # Still considered a successful run
    mock_setup["mock_loader"].get_issues.assert_called_once()
    assert mock_setup["mock_show"].called
