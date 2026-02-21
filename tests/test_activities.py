"""Tests for GET /activities endpoint"""

import pytest


class TestGetActivities:
    """Test suite for retrieving activities"""

    def test_get_activities_returns_200(self, client):
        """Test that /activities endpoint returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that /activities endpoint returns a dictionary"""
        response = client.get("/activities")
        activities = response.json()
        assert isinstance(activities, dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that returned activities include expected names"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_details in activities.items():
            for field in required_fields:
                assert field in activity_details, f"{field} missing from {activity_name}"

    def test_activity_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_details["participants"], list), \
                f"participants for {activity_name} is not a list"

    def test_activity_max_participants_is_int(self, client):
        """Test that max_participants is an integer"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_details["max_participants"], int), \
                f"max_participants for {activity_name} is not an integer"

    def test_initial_participants_are_populated(self, client):
        """Test that some activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
