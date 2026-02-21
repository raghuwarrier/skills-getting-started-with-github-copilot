"""Tests for POST /activities/{activity_name}/signup endpoint"""

import pytest


class TestSignupForActivity:
    """Test suite for signing up for activities"""

    def test_signup_returns_200(self, client, sample_activity):
        """Test that successful signup returns 200 status code"""
        response = client.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, sample_activity):
        """Test that successful signup returns a success message"""
        response = client.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        data = response.json()
        assert "message" in data
        assert sample_activity["email"] in data["message"]
        assert sample_activity["name"] in data["message"]

    def test_signup_adds_participant(self, client, sample_activity):
        """Test that signup adds the email to participants list"""
        # Get initial participants count
        response = client.get("/activities")
        initial_count = len(response.json()[sample_activity["name"]]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        
        # Check participants count increased
        response = client.get("/activities")
        new_count = len(response.json()[sample_activity["name"]]["participants"])
        assert new_count == initial_count + 1
        assert sample_activity["email"] in response.json()[sample_activity["name"]]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_duplicate_signup_returns_400(self, client):
        """Test that signing up twice returns 400 error"""
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@example.com"}
        )
        assert response1.status_code == 200
        
        # Try to sign up again
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@example.com"}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_duplicate_existing_participant_returns_400(self, client):
        """Test that signing up again as existing participant returns 400"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_multiple_different_students(self, client):
        """Test that multiple different students can sign up for same activity"""
        students = ["student1@example.com", "student2@example.com", "student3@example.com"]
        
        for student in students:
            response = client.post(
                "/activities/Programming Class/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Verify all students are signed up
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        for student in students:
            assert student in participants

    def test_signup_different_activities_same_student(self, client):
        """Test that same student can sign up for multiple activities"""
        email = "multi@example.com"
        activities = ["Chess Club", "Programming Class", "Art Studio"]
        
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email in data[activity]["participants"]

    def test_signup_url_encoding_handles_special_chars(self, client):
        """Test that activities with special chars are handled correctly"""
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 200
