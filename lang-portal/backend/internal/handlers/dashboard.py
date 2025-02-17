from flask import jsonify
from flask_restful import Resource
from internal.models.models import (
    db, StudySession, StudyActivity, Group, 
    Word, WordReviewItem
)
from sqlalchemy import func, distinct, case
from datetime import datetime, timedelta

class LastStudySessionAPI(Resource):
    def get(self):
        """GET /api/dashboard/last_study_session"""
        last_session = db.session.query(
            StudySession,
            Group.name.label('group_name'),
            StudyActivity.id.label('study_activity_id')
        ).join(StudySession.group)\
         .join(StudySession.study_activity)\
         .order_by(StudySession.created_at.desc())\
         .first()
        
        if not last_session:
            return {'message': 'No study sessions found'}, 404
            
        return {
            'id': last_session.StudySession.id,
            'group_id': last_session.StudySession.group_id,
            'group_name': last_session.group_name,
            'created_at': last_session.StudySession.created_at.isoformat(),
            'study_activity_id': last_session.study_activity_id
        }

class StudyProgressAPI(Resource):
    def get(self):
        """GET /api/dashboard/study_progress"""
        # Get total unique words studied
        words_studied = db.session.query(
            func.count(distinct(WordReviewItem.word_id))
        ).scalar()
        
        # Get total available words
        total_words = db.session.query(func.count(Word.id)).scalar()
        
        return {
            'total_words_studied': words_studied or 0,
            'total_available_words': total_words or 0
        }

class QuickStatsAPI(Resource):
    def get(self):
        """GET /api/dashboard/quick_stats"""
        # Calculate success rate
        stats = db.session.query(
            func.count(case((WordReviewItem.correct == True, 1))).label('correct'),
            func.count(WordReviewItem.id).label('total')
        ).first()
        
        success_rate = (stats.correct / stats.total * 100) if stats.total > 0 else 0
        
        # Get total study sessions
        total_sessions = db.session.query(func.count(StudySession.id)).scalar()
        
        # Get total active groups (groups with study sessions)
        active_groups = db.session.query(
            func.count(distinct(StudySession.group_id))
        ).scalar()
        
        # Calculate study streak (consecutive days with study sessions)
        streak = self._calculate_streak()
        
        return {
            'success_rate': round(success_rate, 1),
            'total_study_sessions': total_sessions or 0,
            'total_active_groups': active_groups or 0,
            'study_streak_days': streak
        }
    
    def _calculate_streak(self):
        """Helper method to calculate study streak"""
        today = datetime.utcnow().date()
        streak = 0
        current_date = today
        
        while True:
            # Check if there are any study sessions for the current date
            has_session = db.session.query(StudySession).filter(
                func.date(StudySession.created_at) == current_date
            ).first() is not None
            
            if not has_session:
                break
                
            streak += 1
            current_date = current_date - timedelta(days=1)
        
        return streak 