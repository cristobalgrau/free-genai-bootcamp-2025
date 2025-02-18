import pytest
from flask.testing import FlaskClient
import json

class TestDashboardEndpoints:
    def test_last_study_session(self, client: FlaskClient, setup_study_session):
        """Test GET /api/dashboard/last_study_session"""
        response = client.get('/api/dashboard/last_study_session')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure
        assert isinstance(data.get('id'), int)
        assert isinstance(data.get('group_id'), int)
        assert isinstance(data.get('group_name'), str)
        assert isinstance(data.get('created_at'), str)
        assert isinstance(data.get('study_activity_id'), int)

    def test_study_progress(self, client: FlaskClient):
        """Test GET /api/dashboard/study_progress"""
        response = client.get('/api/dashboard/study_progress')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert isinstance(data.get('total_words_studied'), int)
        assert isinstance(data.get('total_available_words'), int)

    def test_quick_stats(self, client: FlaskClient):
        """Test GET /api/dashboard/quick_stats"""
        response = client.get('/api/dashboard/quick_stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Success rate could be integer 0 when no studies exist
        assert isinstance(data.get('success_rate'), (int, float))
        assert isinstance(data.get('total_study_sessions'), int)
        assert isinstance(data.get('total_active_groups'), int)
        assert isinstance(data.get('study_streak_days'), int)