from flask import jsonify
from flask_restful import Resource
from internal.models.models import db
from sqlalchemy import text

class WordListAPI(Resource):
    def get(self):
        """GET /api/words - Returns all words with pagination"""
        try:
            query = """
                SELECT 
                    w.*,
                    COUNT(CASE WHEN wri.correct = 1 THEN 1 END) as correct_count,
                    COUNT(CASE WHEN wri.correct = 0 THEN 1 END) as wrong_count
                FROM words w
                LEFT JOIN word_review_items wri ON w.id = wri.word_id
                GROUP BY w.id;
            """
            
            words = db.session.execute(text(query)).fetchall()
            
            return {
                "items": [{
                    "id": word[0],
                    "kanji": word[1],
                    "romaji": word[2],
                    "english": word[3],
                    "parts": word[4],
                    "correct_count": word[5] or 0,
                    "wrong_count": word[6] or 0
                } for word in words],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "total_items": len(words),
                    "items_per_page": 100
                }
            }
        except Exception as e:
            print(f"Error in WordListAPI: {str(e)}")
            return {"error": str(e)}, 500

class WordAPI(Resource):
    def get(self, word_id):
        """GET /api/words/:id - Returns detailed information about a specific word"""
        try:
            result = db.session.execute(
                text("SELECT * FROM words WHERE id = :id"),
                {"id": word_id}
            ).fetchone()
            
            if not result:
                return {"error": "Word not found"}, 404
                
            return {
                "id": result[0],
                "kanji": result[1],
                "romaji": result[2],
                "english": result[3],
                "parts": result[4]
            }
        except Exception as e:
            print(f"Error in WordAPI: {str(e)}")
            return {"error": str(e)}, 500