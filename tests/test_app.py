import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app import app, activities

client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(
        {
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
        }
    )


def test_signup_allows_space_available():
    reset_activities()

    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

    assert response.status_code == 200
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_when_activity_is_full():
    reset_activities()
    activities["Chess Club"]["participants"] = [
        f"student{i}@mergington.edu" for i in range(12)
    ]

    response = client.post("/activities/Chess Club/signup?email=overflow@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_rejects_duplicate_registration():
    reset_activities()

    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_then_signup_allows_reentry():
    reset_activities()
    activities["Chess Club"]["participants"] = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu",
        "student4@mergington.edu",
        "student5@mergington.edu",
        "student6@mergington.edu",
        "student7@mergington.edu",
        "student8@mergington.edu",
        "student9@mergington.edu",
        "student10@mergington.edu",
        "student11@mergington.edu",
    ]

    delete_response = client.delete(
        "/activities/Chess Club/unregister?email=student11@mergington.edu"
    )
    assert delete_response.status_code == 200

    signup_response = client.post(
        "/activities/Chess Club/signup?email=student11@mergington.edu"
    )

    assert signup_response.status_code == 200
    assert "student11@mergington.edu" in activities["Chess Club"]["participants"]
