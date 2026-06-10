"""Tests for the FastAPI application endpoints."""

import pytest


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to /static/index.html."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]

        # Assert
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_adds_participant(self, client):
        """Test that a student can sign up for an activity."""
        # Arrange
        email = "test@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up test@mergington.edu" in data["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_registration_fails(self, client):
        """Test that a student cannot register twice for the same activity."""
        # Arrange
        email = "duplicate@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )

        # Assert - First signup succeeds
        assert response1.status_code == 200

        # Act - Second signup
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )

        # Assert - Second signup fails
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup fails for non-existent activity."""
        # Arrange
        email = "test@mergington.edu"

        # Act
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_with_different_activities_succeeds(self, client):
        """Test that the same student can sign up for different activities."""
        # Arrange
        email = "student@mergington.edu"
        
        # Act - Sign up for first activity
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )

        # Assert - First signup succeeds
        assert response1.status_code == 200

        # Act - Sign up for second activity
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )

        # Assert - Second signup succeeds
        assert response2.status_code == 200

        # Verify both signups were successful
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_removes_participant(self, client):
        """Test that a participant can be unregistered from an activity."""
        # Arrange
        email = "unregister@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")

        # Act
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

        # Verify removal
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_not_registered_fails(self, client):
        """Test that unregistering a non-registered student fails."""
        # Arrange
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister fails for non-existent activity."""
        # Arrange
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_works_multiple_times(self, client):
        """Test that multiple participants can be unregistered from an activity."""
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email1}")
        client.post(f"/activities/Programming%20Class/signup?email={email2}")

        # Act - Unregister first student
        response1 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email1}"
        )

        # Assert - First unregister succeeds
        assert response1.status_code == 200

        # Act - Unregister second student
        response2 = client.delete(
            f"/activities/Programming%20Class/unregister?email={email2}"
        )

        # Assert - Second unregister succeeds
        assert response2.status_code == 200

        # Verify both are unregistered
        activities = client.get("/activities").json()
        assert email1 not in activities["Chess Club"]["participants"]
        assert email2 not in activities["Programming Class"]["participants"]
