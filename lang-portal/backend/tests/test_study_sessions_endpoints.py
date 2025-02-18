from flask.testing import FlaskClient
import json
from datetime import datetime
from tests.utils.validation import ResponseValidator

class TestStudySessionsEndpoints:
    def test_get_study_sessions_list(self, client: FlaskClient):
        """Test GET /api/study_sessions"""
        response = client.get('/api/study_sessions')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'items' in data
        for session in data['items']:
            assert 'activity_name' in session
            assert 'created_at' in session

    def test_get_study_session_details(self, client: FlaskClient, setup_study_session):
        """Test GET /api/study_sessions/:id"""
        session_id = setup_study_session['id']
        response = client.get(f'/api/study_sessions/{session_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert isinstance(data.get('id'), int)
        assert isinstance(data.get('activity_name'), str)
        assert isinstance(data.get('group_name'), str)

    def test_get_study_session_words(self, client: FlaskClient, setup_study_session):
        """Test GET /api/study_sessions/:id/words"""
        session_id = setup_study_session['id']
        response = client.get(f'/api/study_sessions/{session_id}/words')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'items' in data
        assert 'pagination' in data
        for word in data['items']:
            assert 'japanese' in word
            assert 'romaji' in word
            assert 'english' in word
            assert isinstance(word['correct_count'], int)
            assert isinstance(word['wrong_count'], int)

    def test_record_word_review(self, client: FlaskClient):
        """Test POST /api/study_sessions/:id/words/:word_id/review"""
        payload = {"correct": True}
        response = client.post('/api/study_sessions/1/words/1/review',
                             json=payload)
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        
        # Check if either success or word_id is present (depending on API implementation)
        assert any(key in data for key in ['success', 'word_id'])
        if 'word_id' in data:
            assert isinstance(data['word_id'], int)
        assert isinstance(data['study_session_id'], int)
        assert isinstance(data['correct'], bool)
        assert isinstance(datetime.fromisoformat(data['created_at']), datetime)