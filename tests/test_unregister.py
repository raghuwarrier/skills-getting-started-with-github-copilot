"""Tests for DELETE /activities/{activity_name}/unregister endpoint"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for unregistering from activities"""

    def test_unregister_returns_200(self, client):
        """Test that successful unregister returns 200 status code"""
        # First sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "unregister@example.com"}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "unregister@example.com"}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client):
        """Test that successful unregister returns a success message"""
        # First sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "unregister@example.com"}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "unregister@example.com"}
        )
        data = response.json()
        assert "message" in data
        assert "unregister" in data["message"].lower() or "unregistered" in data["message"].lower()

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the email from participants list"""
        email = "remove@example.com"
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # michael@mergington.edu is initially in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered_returns_400(self, client):
        """Test that unregistering when not signed up returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@example.com"}
        )
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "not registered" in detail or "not signed up" in detail

    def test_unregister_then_signup_again(self, client):
        """Test that student can sign up again after unregistering"""
        email = "resignup@example.com"
        
        # Sign up
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]

    def test_unregister_multiple_times_fails_second_time(self, client):
        """Test that unregistering twice returns error on second attempt"""
        email = "double@example.com"
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # First unregister
        response1 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 400

    def test_unregister_url_encoding_handles_special_chars(self, client):
        """Test that unregister handles URL encoding correctly"""
        # Sign up for Programming Class (has space in name)
        client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "test@example.com"}
        )
        
        # Unregister with encoded name
        response = client.delete(
            "/activities/Programming%20Class/unregister",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 200

    def test_unregister_reduces_spot_count(self, client):
        """Test that unregistering increases available spots"""
        email = "spots@example.com"
        
        # Get initial available spots
        response = client.get("/activities")
        initial_spots = response.json()["Chess Club"]["max_participants"] - len(
            response.json()["Chess Club"]["participants"]
        )
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Check spots decreased
        response = client.get("/activities")
        after_signup_spots = response.json()["Chess Club"]["max_participants"] - len(
            response.json()["Chess Club"]["participants"]
        )
        assert after_signup_spots == initial_spots - 1
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Check spots increased back
        response = client.get("/activities")
        after_unregister_spots = response.json()["Chess Club"]["max_participants"] - len(
            response.json()["Chess Club"]["participants"]
        )
        assert after_unregister_spots == initial_spots
