import pytest
from models.model import Event, Issue, State
from datetime import datetime

# Fixture that returns a mock issue with one event in its timeline
@pytest.fixture(scope='function')
def sample_issue_data(sample_event_data):
    return {
        "url": "https://hauntedhub.io/repos/phantom-poetry/issues/800",
        "creator": "ghostwriter42",
        "labels": [
            "kind/paranormal",
            "status/possessed"
        ],
        "state": "open",
        "assignees": ["captain-obvious", "ghost-in-the-shell"],
        "title": "removed dependency keeps coming back",
        "text": (
            "We deleted it. We purged it. We even chanted `pip uninstall` three times in a mirror. "
            "But `hauntlib` keeps returning to `requirements.txt` like it never left."
        ),
        "number": 800,
        "created_date": "2025-10-31T04:00:00Z",
        "updated_date": "2025-10-31T04:06:06Z",
        "timeline_url": "https://hauntedhub.io/api/repos/phantom-poetry/issues/800/timeline",
        "events": [sample_event_data]  # Event fixture included here
    }

# Fixture that returns a single mock event associated with an issue
@pytest.fixture(scope='function')
def sample_event_data():
    return {
        "event_type": "commented",
        "event_date": "2025-04-03T00:06:06Z",
        "author": "ghost-in-the-shell",
        "label": "kind/paranormal",
        "comment": "This bug only manifests under moonlight. Recommend holy water or switching to dark mode."
    }

# Test Event constructor with empty data to ensure all fields default to None
def test_event_constructor():
    event = Event({})
    assert event.event_type is None
    assert event.author is None
    assert event.event_date is None
    assert event.label is None
    assert event.comment is None

# Test Event constructor with valid data to verify correct parsing
def test_event_valid_data(sample_event_data):
    event = Event(sample_event_data)
    assert event.event_type == 'commented'
    assert event.author == 'ghost-in-the-shell'
    assert isinstance(event.event_date, datetime)  # Check datetime parsing
    assert event.label == 'kind/paranormal'
    assert event.comment == (
        "This bug only manifests under moonlight. Recommend holy water or switching to dark mode."
    )

# Test Event constructor with malformed date string to ensure it handles parsing failure
def test_event_malformed_date():
    event = Event({"event_date": "She brought tarot cards, no date T_T"})
    assert event.event_date is None

# Test Issue constructor with None input to ensure all fields fall back to safe defaults
def test_issue_constructor():
    issue = Issue(None)
    assert issue.url is None
    assert issue.creator is None
    assert len(issue.labels) == 0
    assert issue.state is None
    assert len(issue.assignees) == 0
    assert issue.title is None
    assert issue.text is None
    assert issue.number == -1  # Sentinel value for missing number
    assert issue.created_date is None
    assert issue.updated_date is None
    assert issue.timeline_url is None
    assert len(issue.events) == 0

# Test Issue constructor with full, valid input to ensure fields are correctly parsed
def test_issue_valid_data(sample_issue_data):
    issue = Issue(sample_issue_data)
    assert issue.url == "https://hauntedhub.io/repos/phantom-poetry/issues/800"
    assert issue.creator == "ghostwriter42"
    assert issue.labels == ["kind/paranormal", "status/possessed"]
    assert issue.state == State.open  # Assumes mapping string "open" to Enum
    assert issue.assignees == ["captain-obvious", "ghost-in-the-shell"]
    assert issue.title == "removed dependency keeps coming back"
    assert issue.text.startswith("We deleted it")  # Check long string
    assert issue.number == 800
    assert isinstance(issue.created_date, datetime)
    assert isinstance(issue.updated_date, datetime)
    assert issue.timeline_url == "https://hauntedhub.io/api/repos/phantom-poetry/issues/800/timeline"
    assert len(issue.events) == 1
    assert isinstance(issue.events[0], Event)

# Test fallback when 'number' field is non-numeric (should be -1)
def test_issue_malformed_number():
    issue = Issue({
        "number": "What? I\'m not funny all the time",  # Invalid number
        "state": "open"
    })
    assert issue.number == -1
