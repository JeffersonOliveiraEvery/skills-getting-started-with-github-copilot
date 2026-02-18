import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_returns_activity_details(self, client):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        activities = response.json()
        chess = activities["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
    
    def test_get_activities_shows_participants(self, client):
        """Test that participants list is included"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_to_participants_list(self, client):
        """Test that signup actually adds to participants"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3
    
    def test_signup_duplicate_participant_fails(self, client):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test signing up multiple different students"""
        client.post("/activities/Programming Class/signup?email=alice@mergington.edu")
        client.post("/activities/Programming Class/signup?email=bob@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        participants = activities["Programming Class"]["participants"]
        assert "alice@mergington.edu" in participants
        assert "bob@mergington.edu" in participants


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering a participant"""
        response = client.delete(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_from_list(self, client):
        """Test that unregister actually removes from participants"""
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1
    
    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering non-existent participant fails"""
        response = client.delete(
            "/activities/Chess Club/signup?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static content"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_unregister_flow(self, client):
        """Test complete signup and unregister workflow"""
        # Sign up
        response = client.post(
            "/activities/Gym Class/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify it's added
        response = client.get("/activities")
        assert "test@mergington.edu" in response.json()["Gym Class"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Gym Class/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify it's removed
        response = client.get("/activities")
        assert "test@mergington.edu" not in response.json()["Gym Class"]["participants"]
    
    def test_signup_after_unregister(self, client):
        """Test that student can sign up again after unregistering"""
        # Unregister existing participant
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        # Sign them back up
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify they're back
        response = client.get("/activities")
        assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]
