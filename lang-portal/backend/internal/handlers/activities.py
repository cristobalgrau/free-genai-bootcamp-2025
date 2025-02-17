from flask import jsonify, request
from flask_restful import Resource
from internal.models.models import db, StudyActivity, StudySession
from sqlalchemy import func

class StudyActivityListAPI(Resource):
    def get(self):
        """GET /api/study_activities - Returns all study activities"""
        activities = db.session.query(
            StudyActivity,
            func.count(StudySession.id).label('total_sessions')
        ).outerjoin(StudyActivity.study_sessions)\
         .group_by(StudyActivity.id)\
         .all()
        
        return {
            'items': [{
                'id': activity.StudyActivity.id,
                'name': activity.StudyActivity.name,
                'thumbnail_url': activity.StudyActivity.thumbnail_url,
                'description': activity.StudyActivity.description,
                'total_sessions': activity.total_sessions
            } for activity in activities]
        }

    def post(self):
        """POST /api/study_activities - Creates a new study activity"""
        data = request.get_json()
        
        if not data or 'name' not in data:
            return {'error': 'Name is required'}, 400
            
        activity = StudyActivity(
            name=data['name'],
            thumbnail_url=data.get('thumbnail_url'),
            description=data.get('description')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return {
            'id': activity.id,
            'name': activity.name,
            'thumbnail_url': activity.thumbnail_url,
            'description': activity.description
        }, 201

class StudyActivityAPI(Resource):
    def get(self, activity_id):
        """GET /api/study_activities/:id - Returns details about a specific activity"""
        activity = StudyActivity.query.get_or_404(activity_id)
        
        # Get usage statistics
        stats = db.session.query(
            func.count(StudySession.id).label('total_sessions'),
            func.count(func.distinct(StudySession.group_id)).label('unique_groups')
        ).filter(StudySession.study_activity_id == activity_id)\
         .first()
        
        return {
            'id': activity.id,
            'name': activity.name,
            'thumbnail_url': activity.thumbnail_url,
            'description': activity.description,
            'stats': {
                'total_sessions': stats.total_sessions,
                'unique_groups': stats.unique_groups
            }
        }

    def put(self, activity_id):
        """PUT /api/study_activities/:id - Updates a study activity"""
        activity = StudyActivity.query.get_or_404(activity_id)
        data = request.get_json()
        
        if not data:
            return {'error': 'No data provided'}, 400
            
        activity.name = data.get('name', activity.name)
        activity.thumbnail_url = data.get('thumbnail_url', activity.thumbnail_url)
        activity.description = data.get('description', activity.description)
        
        db.session.commit()
        
        return {
            'id': activity.id,
            'name': activity.name,
            'thumbnail_url': activity.thumbnail_url,
            'description': activity.description
        }

    def delete(self, activity_id):
        """DELETE /api/study_activities/:id - Deletes a study activity"""
        activity = StudyActivity.query.get_or_404(activity_id)
        
        # Check if activity has any sessions
        has_sessions = db.session.query(StudySession)\
            .filter(StudySession.study_activity_id == activity_id)\
            .first() is not None
            
        if has_sessions:
            return {
                'error': 'Cannot delete activity that has study sessions'
            }, 400
        
        db.session.delete(activity)
        db.session.commit()
        
        return '', 204 