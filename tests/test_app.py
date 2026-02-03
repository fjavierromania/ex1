"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test cases for the activities endpoint"""

    def test_get_activities_returns_list(self):
        """Test that GET /activities returns a list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
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
    """Test cases for the signup endpoint"""

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_duplicate_email_fails(self):
        """Test that duplicate signup is rejected"""
        email = "test-dup@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_updates_participant_count(self):
        """Test that signup updates the participant count"""
        activity = "Programming Class"
        email = "newstudent@mergington.edu"

        # Get initial participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity]["participants"])

        # Sign up
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )

        # Check updated count
        response_after = client.get("/activities")
        updated_count = len(response_after.json()[activity]["participants"])

        assert updated_count == initial_count + 1


class TestUnregister:
    """Test cases for the unregister endpoint"""

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        activity = "Tennis Club"
        email = "unregister-test@mergington.edu"

        # First, sign up
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )

        # Then unregister
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregister from nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_not_signed_up_fails(self):
        """Test that unregister fails if student not signed up"""
        activity = "Drama Club"
        email = "notsignedup@mergington.edu"

        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        activity = "Science Club"
        email = "remove-me@mergington.edu"

        # Sign up
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )

        # Get count before unregister
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])

        # Unregister
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )

        # Get count after unregister
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity]["participants"])

        assert count_after == count_before - 1
        assert email not in response_after.json()[activity]["participants"]


class TestRoot:
    """Test cases for the root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
