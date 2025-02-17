from flask import jsonify, request
from flask_restful import Resource
from internal.models.models import db, WordReviewItem, Word
from sqlalchemy import func

class WordReviewListAPI(Resource):
    def get(self):
        """GET /api/word_reviews - Returns all word reviews"""
        reviews = db.session.query(WordReviewItem).all()
        
        return {
            'items': [{
                'id': review.id,
                'word_id': review.word_id,
                'study_session_id': review.study_session_id,
                'correct': review.correct,
                'created_at': review.created_at.isoformat()
            } for review in reviews]
        }

    def post(self):
        """POST /api/word_reviews - Creates a new word review"""
        data = request.get_json()
        
        if not data or 'word_id' not in data or 'study_session_id' not in data or 'correct' not in data:
            return {'error': 'Word ID, Study Session ID, and Correct fields are required'}, 400
            
        review = WordReviewItem(
            word_id=data['word_id'],
            study_session_id=data['study_session_id'],
            correct=data['correct']
        )
        
        db.session.add(review)
        db.session.commit()
        
        return {
            'id': review.id,
            'word_id': review.word_id,
            'study_session_id': review.study_session_id,
            'correct': review.correct,
            'created_at': review.created_at.isoformat()
        }, 201

class WordReviewSessionAPI(Resource):
    def post(self, session_id, word_id):
        """POST /api/study_sessions/:session_id/words/:word_id/review - Creates a review tied to a session"""
        data = request.get_json()
        
        if not data or 'correct' not in data:
            return {'error': 'Correct field is required'}, 400
            
        review = WordReviewItem(
            word_id=word_id,
            study_session_id=session_id,
            correct=data['correct']
        )
        
        db.session.add(review)
        db.session.commit()
        
        return {
            'id': review.id,
            'word_id': review.word_id,
            'study_session_id': review.study_session_id,
            'correct': review.correct,
            'created_at': review.created_at.isoformat()
        }, 201

class WordReviewAPI(Resource):
    def get(self, review_id):
        """GET /api/word_reviews/:id - Returns details about a specific review"""
        review = WordReviewItem.query.get_or_404(review_id)
        
        return {
            'id': review.id,
            'word_id': review.word_id,
            'study_session_id': review.study_session_id,
            'correct': review.correct,
            'created_at': review.created_at.isoformat()
        }

    def delete(self, review_id):
        """DELETE /api/word_reviews/:id - Deletes a word review"""
        review = WordReviewItem.query.get_or_404(review_id)
        
        db.session.delete(review)
        db.session.commit()
        
        return '', 204 