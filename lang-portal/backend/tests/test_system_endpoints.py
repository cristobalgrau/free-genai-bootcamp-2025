from flask.testing import FlaskClient
import json

class TestSystemEndpoints:
    def test_reset_history(self, client: FlaskClient):
        """Test POST /api/reset_history"""
        response = client.post('/api/reset_history')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['message'] == "Study history has been reset"

    def test_full_reset(self, client: FlaskClient):
        """Test POST /api/full_reset"""
        response = client.post('/api/full_reset')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['message'] == "System has been fully reset"