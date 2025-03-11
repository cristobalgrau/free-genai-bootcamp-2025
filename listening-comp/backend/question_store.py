import json
import os
from datetime import datetime

class QuestionStore:
    def __init__(self):
        self.store_path = os.path.join(os.path.dirname(__file__), 'stored_questions.json')
        self._ensure_store_exists()

    def _ensure_store_exists(self):
        if not os.path.exists(self.store_path):
            with open(self.store_path, 'w') as f:
                json.dump([], f)

    def save_question(self, question_data, practice_type):
        try:
            with open(self.store_path, 'r') as f:
                questions = json.load(f)
            
            questions.append({
                'id': len(questions),
                'timestamp': datetime.now().isoformat(),
                'practice_type': practice_type,
                'question_data': question_data,
            })
            
            with open(self.store_path, 'w') as f:
                json.dump(questions, f, indent=2)
            
            return True
        except Exception:
            return False

    def get_all_questions(self):
        try:
            with open(self.store_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def get_question_by_id(self, question_id):
        questions = self.get_all_questions()
        for question in questions:
            if question['id'] == question_id:
                return question
        return None
