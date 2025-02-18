from flask.testing import FlaskClient
import json
from typing import Dict, Any

class TestGroupsEndpoints:
    def test_get_groups_list(self, client: FlaskClient):
        """Test GET /api/groups with pagination"""
        response = client.get('/api/groups')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'items' in data
        assert 'pagination' in data
        pagination = data['pagination']
        assert pagination['items_per_page'] == 100
        
        for item in data['items']:
            assert isinstance(item['id'], int)
            assert isinstance(item['word_count'], int)

    def test_get_group_details(self, client: FlaskClient, sample_group):
        """Test GET /api/groups/:id"""
        response = client.get(f'/api/groups/{sample_group["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == sample_group['id']
        assert data['name'] == sample_group['name']
        assert 'stats' in data
        assert isinstance(data['stats']['total_word_count'], int)

    def test_get_group_words(self, client: FlaskClient):
        """Test GET /api/groups/:id/words"""
        response = client.get('/api/groups/1/words')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'items' in data
        for item in data['items']:
            assert 'kanji' in item
            assert 'english' in item
            assert 'correct_count' in item

    def test_get_group_study_sessions(self, client: FlaskClient):
        """Test GET /api/groups/:id/study_sessions"""
        response = client.get('/api/groups/1/study_sessions')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'items' in data
        for session in data['items']:
            assert 'activity_name' in session
            assert 'created_at' in session