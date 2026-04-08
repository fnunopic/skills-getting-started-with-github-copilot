"""
Comprehensive tests for the Mergington High School API using AAA pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_success(self):
        """Test successfully retrieving all activities"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball" in data
    
    def test_get_activities_structure(self):
        """Test that activities have the correct structure"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_info in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)
    
    def test_get_activities_contains_expected_fields(self):
        """Test that each activity contains all required fields"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) > 0


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        """Test successfully signing up for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_url = "/activities/Chess%20Club/signup"
        
        # Act
        response = client.post(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Art Club"
        activity_url = f"/activities/{activity.replace(' ', '%20')}/signup"
        
        # Act - Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Act - Sign up
        client.post(activity_url, params={"email": email})
        
        # Act - Check final count
        response2 = client.get("/activities")
        final_data = response2.json()[activity]
        
        # Assert
        assert len(final_data["participants"]) == initial_count + 1
        assert email in final_data["participants"]
    
    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        activity_url = "/activities/Nonexistent%20Activity/signup"
        
        # Act
        response = client.post(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_signed_up(self):
        """Test that a student cannot sign up twice for the same activity"""
        # Arrange
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity_url = "/activities/Chess%20Club/signup"
        
        # Act
        response = client.post(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_different_activities(self):
        """Test that a student can sign up for multiple different activities"""
        # Arrange
        email = "versatile@mergington.edu"
        chess_url = "/activities/Chess%20Club/signup"
        drama_url = "/activities/Drama%20Club/signup"
        
        # Act
        response1 = client.post(chess_url, params={"email": email})
        response2 = client.post(drama_url, params={"email": email})
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    def test_signup_persists_across_requests(self):
        """Test that signups persist across multiple requests"""
        # Arrange
        email = "persistent@mergington.edu"
        activity = "Tennis"
        activity_url = f"/activities/{activity}/signup"
        
        # Act
        client.post(activity_url, params={"email": email})
        response = client.get("/activities")
        
        # Assert
        assert email in response.json()[activity]["participants"]


class TestCancelSignupEndpoint:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_cancel_signup_success(self):
        """Test successfully canceling signup"""
        # Arrange
        email = "test_cancel@mergington.edu"
        activity_url = "/activities/Programming%20Class/signup"
        
        # Act - First sign up
        client.post(activity_url, params={"email": email})
        
        # Act - Then cancel
        response = client.delete(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_cancel_signup_removes_participant(self):
        """Test that cancel signup actually removes the participant"""
        # Arrange
        email = "remove_me@mergington.edu"
        activity = "Science Olympiad"
        activity_url = f"/activities/{activity.replace(' ', '%20')}/signup"
        
        # Act - Sign up
        client.post(activity_url, params={"email": email})
        
        # Act - Get count before cancel
        response1 = client.get("/activities")
        before_count = len(response1.json()[activity]["participants"])
        
        # Act - Cancel
        client.delete(activity_url, params={"email": email})
        
        # Act - Check count after cancel
        response2 = client.get("/activities")
        after_data = response2.json()[activity]
        
        # Assert
        assert len(after_data["participants"]) == before_count - 1
        assert email not in after_data["participants"]
    
    def test_cancel_signup_nonexistent_activity(self):
        """Test canceling signup for non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        activity_url = "/activities/Nonexistent%20Activity/signup"
        
        # Act
        response = client.delete(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_cancel_signup_not_signed_up(self):
        """Test canceling signup when student is not signed up"""
        # Arrange
        email = "not_signed_up@mergington.edu"
        activity_url = "/activities/Chess%20Club/signup"
        
        # Act
        response = client.delete(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]


class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_signup_with_missing_email(self):
        """Test signup request without email parameter"""
        # Arrange
        activity_url = "/activities/Chess%20Club/signup"
        
        # Act
        response = client.post(activity_url)
        
        # Assert
        assert response.status_code == 422
    
    def test_cancel_signup_with_missing_email(self):
        """Test cancel signup request without email parameter"""
        # Arrange
        activity_url = "/activities/Chess%20Club/signup"
        
        # Act
        response = client.delete(activity_url)
        
        # Assert
        assert response.status_code == 422
    
    def test_signup_with_empty_activity_name(self):
        """Test signup with empty activity name"""
        # Arrange
        email = "student@mergington.edu"
        activity_url = "/activities//signup"
        
        # Act
        response = client.post(activity_url, params={"email": email})
        
        # Assert
        assert response.status_code == 404  # Empty activity name is treated as non-existent
    
    def test_get_activities_returns_json(self):
        """Test that activities endpoint returns valid JSON"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.headers["content-type"] == "application/json"


class TestDataIntegrity:
    """Tests to ensure data integrity"""
    
    def test_all_activities_have_max_participants(self):
        """Test that all activities have a max_participants value"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_info in data.items():
            assert "max_participants" in activity_info
            assert isinstance(activity_info["max_participants"], int)
            assert activity_info["max_participants"] > 0
    
    def test_participants_count_doesn_exceed_max(self):
        """Test that participants don't exceed max_participants (for existing data)"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_info in data.items():
            assert len(activity_info["participants"]) <= activity_info["max_participants"], \
                f"{activity_name} has more participants than allowed"