import json
import os
from datetime import datetime
from .audio_generator import AudioGenerator

class QuestionStore:
    def __init__(self):
        # Create data directory path inside backend folder
        backend_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(backend_dir, 'data')
        self.audio_dir = os.path.join(self.data_dir, 'audio')
        self.store_path = os.path.join(self.data_dir, 'stored_questions.json')
        self._ensure_store_exists()

    def _ensure_store_exists(self):
        # Create data and audio directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        
        if not os.path.exists(self.store_path):
            with open(self.store_path, 'w') as f:
                json.dump([], f)

    def save_question(self, question_data, practice_type):
        try:
            with open(self.store_path, 'r') as f:
                questions = json.load(f)
            
            question_id = len(questions)
            audio_path = os.path.abspath(os.path.join(self.audio_dir, f'question_{question_id}.mp3'))
            
            # Ensure audio directory exists
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            # Generate audio file
            audio_gen = AudioGenerator()
            # Pass the full question_data to generate audio
            audio_gen.generate_conversation_audio(
                question_data, 
                audio_path
            )
            
            questions.append({
                'id': question_id,
                'timestamp': datetime.now().isoformat(),
                'practice_type': practice_type,
                'question_data': question_data,
                'audio_path': audio_path  # Store absolute path
            })
            
            with open(self.store_path, 'w') as f:
                json.dump(questions, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving question: {e}")
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

