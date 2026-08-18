from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


BASE_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Club": {
        "description": "Practice soccer skills and compete in friendly matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 24,
        "participants": [],
    },
    "Track and Field": {
        "description": "Develop running, jumping, and throwing skills",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 30,
        "participants": [],
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
    },
    "Theater Club": {
        "description": "Develop acting skills and perform in school productions",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": [],
    },
    "Debate Club": {
        "description": "Build public speaking and critical thinking skills",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": [],
    },
    "Science Club": {
        "description": "Explore scientific topics through experiments and projects",
        "schedule": "Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": [],
    },
}


@pytest.fixture(autouse=True)
def reset_activities_state():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASE_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_success(client):
    response = client.post("/activities/Soccer Club/signup?email=newstudent@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up newstudent@mergington.edu for Soccer Club"
    }
    assert "newstudent@mergington.edu" in app_module.activities["Soccer Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_email(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_for_activity_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown Club/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_activity_rejects_full_activity(client):
    app_module.activities["Soccer Club"]["participants"] = [
        f"student{i}@mergington.edu" for i in range(24)
    ]

    response = client.post("/activities/Soccer Club/signup?email=another@mergington.edu")

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_unregister_participant_success(client):
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]
