from typing import Dict, Any, List
from datetime import datetime

class ResponseValidator:
    @staticmethod
    def check_pagination(data: Dict[str, Any], expected_per_page: int = 100) -> bool:
        """Validate pagination structure in response data"""
        if not isinstance(data, dict):
            return False
            
        required_fields = {'items', 'pagination'}
        if not all(field in data for field in required_fields):
            return False
            
        pagination = data['pagination']
        required_pagination_fields = {
            'current_page',
            'total_pages',
            'total_items',
            'items_per_page'
        }
        
        if not all(field in pagination for field in required_pagination_fields):
            return False
            
        return (isinstance(pagination['items_per_page'], int) and 
                pagination['items_per_page'] == expected_per_page)

    @staticmethod
    def check_timestamp(timestamp_str: str) -> bool:
        """Validate ISO 8601 timestamp format"""
        try:
            datetime.fromisoformat(timestamp_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_word(word: Dict[str, Any]) -> bool:
        """Validate word object structure"""
        required_fields = {
            'japanese',
            'romaji',
            'english',
            'correct_count',
            'wrong_count'
        }
        return all(field in word for field in required_fields)