from flask import jsonify, request
from flask_restful import Resource
from internal.models.models import (
    db, StudySession, StudyActivity, Group, 
    Word, WordReviewItem
)
from sqlalchemy import func, case
from datetime import datetime

class StudySessionListAPI(Resource):
    def get(self):
        """GET /api/study_sessions - Returns all study sessions"""
        page = 1  # TODO: Get from request
        per_page = 100
        
        sessions = db.session.query(
            StudySession,
            Group.name.label('group_name'),
            StudyActivity.name.label('activity_name'),
            func.count(WordReviewItem.id).label('review_items_count')
        ).join(StudySession.group)\
         .join(StudySession.study_activity)\
         .outerjoin(StudySession.review_items)\
         .group_by(StudySession.id)\
         .paginate(page=page, per_page=per_page)
        
        return {
            'items': [{
                'id': session.StudySession.id,
                'activity_name': session.activity_name,
                'group_name': session.group_name,
                'start_time': session.StudySession.created_at.isoformat(),
                'review_items_count': session.review_items_count
            } for session in sessions.items],
            'pagination': {
                'current_page': sessions.page,
                'total_pages': sessions.pages,
                'total_items': sessions.total,
                'items_per_page': per_page
            }
        }

    def post(self):
        """POST /api/study_sessions - Creates a new study session"""
        data = request.get_json()
        
        if not data or 'group_id' not in data or 'study_activity_id' not in data:
            return {'error': 'Missing required fields: group_id, study_activity_id'}, 400
            
        # Verify group and activity exist
        group = Group.query.get_or_404(data['group_id'])
        activity = StudyActivity.query.get_or_404(data['study_activity_id'])
        
        # Create new session
        session = StudySession(
            group_id=data['group_id'],
            study_activity_id=data['study_activity_id'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(session)
        db.session.commit()
        
        return {
            'id': session.id,
            'group_id': session.group_id,
            'study_activity_id': session.study_activity_id,
            'created_at': session.created_at.isoformat()
        }, 201

class StudySessionAPI(Resource):
    def get(self, session_id):
        """GET /api/study_sessions/:id - Returns details about a specific study session"""
        session = db.session.query(
            StudySession,
            Group.name.label('group_name'),
            StudyActivity.name.label('activity_name'),
            func.count(WordReviewItem.id).label('review_items_count')
        ).join(StudySession.group)\
         .join(StudySession.study_activity)\
         .outerjoin(StudySession.review_items)\
         .filter(StudySession.id == session_id)\
         .group_by(StudySession.id)\
         .first_or_404()
        
        return {
            'id': session.StudySession.id,
            'activity_name': session.activity_name,
            'group_name': session.group_name,
            'start_time': session.StudySession.created_at.isoformat(),
            'review_items_count': session.review_items_count
        }

class StudySessionWordsAPI(Resource):
    def get(self, session_id):
        """GET /api/study_sessions/:id/words - Returns words reviewed in a study session"""
        page = 1  # TODO: Get from request
        per_page = 100
        
        # Verify session exists
        session = StudySession.query.get_or_404(session_id)
        
        # Get reviewed words with their results
        words = db.session.query(
            Word,
            func.count(case((WordReviewItem.correct == True, 1))).label('correct_count'),
            func.count(case((WordReviewItem.correct == False, 1))).label('wrong_count')
        ).join(WordReviewItem)\
         .filter(WordReviewItem.study_session_id == session_id)\
         .group_by(Word.id)\
         .paginate(page=page, per_page=per_page)
        
        return {
            'items': [{
                'japanese': word.Word.japanese,
                'romaji': word.Word.romaji,
                'english': word.Word.english,
                'correct_count': word.correct_count,
                'wrong_count': word.wrong_count
            } for word in words.items],
            'pagination': {
                'current_page': words.page,
                'total_pages': words.pages,
                'total_items': words.total,
                'items_per_page': per_page
            }
        }

class WordReviewAPI(Resource):
    def post(self, session_id, word_id):
        """POST /api/study_sessions/:id/words/:word_id/review - Records a word review result"""
        # Verify session and word exist
        session = StudySession.query.get_or_404(session_id)
        word = Word.query.get_or_404(word_id)
        
        # Get correct value from request
        data = request.get_json()
        if not data or 'correct' not in data:
            return {'error': 'Missing correct field in request body'}, 400
            
        # Create review item
        review_item = WordReviewItem(
            word_id=word_id,
            study_session_id=session_id,
            correct=data['correct'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(review_item)
        db.session.commit()
        
        return {
            'success': True,
            'word_id': word_id,
            'study_session_id': session_id,
            'correct': review_item.correct,
            'created_at': review_item.created_at.isoformat()
        } 