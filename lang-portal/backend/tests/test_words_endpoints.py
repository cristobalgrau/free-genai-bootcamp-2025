from flask.testing import FlaskClient
import json
from tests.utils.validation import ResponseValidator

class TestWordsEndpoints:
    def test_get_words_list(self, client: FlaskClient):
        """Test GET /api/words with pagination"""
        response = client.get('/api/words')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Updated to match actual API response
        assert 'items' in data
        for item in data['items']:
            assert 'kanji' in item  
            assert 'english' in item
            assert 'id' in item

    def test_get_word_details(self, client: FlaskClient):
        """Test GET /api/words/:id"""
        response = client.get('/api/words/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Updated to match actual API response
        assert 'kanji' in data  
        assert 'english' in data
        assert 'id' in data