"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that /activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_keys(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_chess_club_exists(self):
        """Test that Chess Club activity exists"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_invalid_activity(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_signup_duplicate_email(self):
        """Test that duplicate signup returns error"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Attempt duplicate signup
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "Already signed up" in response2.json()["detail"]

    def test_signup_updates_participants(self):
        """Test that signup adds participant to the list"""
        email = "newstudent@mergington.edu"
        
        # Get initial participants
        initial = client.get("/activities").json()
        initial_count = len(initial["Programming Class"]["participants"])
        
        # Signup
        response = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Check updated participants
        updated = client.get("/activities").json()
        updated_count = len(updated["Programming Class"]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in updated["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "unregister@mergington.edu"
        
        # First signup
        client.post(f"/activities/Gym%20Class/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Gym%20Class/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_invalid_activity(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_student_not_found(self):
        """Test unregister of non-existent student returns 404"""
        response = client.delete(
            "/activities/Soccer%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from list"""
        email = "removeme@mergington.edu"
        
        # Signup
        client.post(f"/activities/Basketball%20Club/signup?email={email}")
        
        # Verify added
        activities = client.get("/activities").json()
        assert email in activities["Basketball Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Basketball%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify removed
        activities = client.get("/activities").json()
        assert email not in activities["Basketball Club"]["participants"]


class TestRootRedirect:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
