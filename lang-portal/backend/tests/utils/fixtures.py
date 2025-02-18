import pytest
from typing import Dict, Any, List
from datetime import datetime, timedelta

@pytest.fixture
def make_paginated_response():
    def _make_paginated_response(
        items: List[Dict[str, Any]],
        current_page: int = 1,
        total_items: int = 100,
        items_per_page: int = 100
    ) -> Dict[str, Any]:
        return {
            "items": items,
            "pagination": {
                "current_page": current_page,
                "total_pages": (total_items + items_per_page - 1) // items_per_page,
                "total_items": total_items,
                "items_per_page": items_per_page
            }
        }
    return _make_paginated_response

@pytest.fixture
def make_study_session():
    def _make_study_session(
        session_id: int,
        start_time: datetime = None
    ) -> Dict[str, Any]:
        if start_time is None:
            start_time = datetime.now()
            
        return {
            "id": session_id,
            "activity_name": "Vocabulary Quiz",
            "group_name": "Basic Greetings",
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(minutes=10)).isoformat(),
            "review_items_count": 20
        }
    return _make_study_session