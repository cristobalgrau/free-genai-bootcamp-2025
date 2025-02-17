from flask import jsonify, request
from flask_restful import Resource
from internal.models.models import db, Group, Word
from sqlalchemy import func

class GroupListAPI(Resource):
    def get(self):
        """GET /api/groups - Returns all groups with word counts"""
        groups = db.session.query(
            Group,
            func.count(Word.id).label('word_count')
        ).outerjoin(Group.words)\
         .group_by(Group.id)\
         .all()
        
        return {
            'items': [{
                'id': group.Group.id,
                'name': group.Group.name,
                'word_count': group.word_count
            } for group in groups]
        }

    def post(self):
        """POST /api/groups - Creates a new group"""
        data = request.get_json()
        
        if not data or 'name' not in data:
            return {'error': 'Name is required'}, 400
            
        group = Group(name=data['name'])
        
        db.session.add(group)
        db.session.commit()
        
        return {
            'id': group.id,
            'name': group.name
        }, 201

class GroupAPI(Resource):
    def get(self, group_id):
        """GET /api/groups/:id - Returns details about a specific group"""
        group = Group.query.get_or_404(group_id)
        
        return {
            'id': group.id,
            'name': group.name,
            'words': [{
                'id': word.id,
                'japanese': word.japanese,
                'romaji': word.romaji,
                'english': word.english
            } for word in group.words]
        }

    def put(self, group_id):
        """PUT /api/groups/:id - Updates a group"""
        group = Group.query.get_or_404(group_id)
        data = request.get_json()
        
        if not data:
            return {'error': 'No data provided'}, 400
            
        group.name = data.get('name', group.name)
        
        db.session.commit()
        
        return {
            'id': group.id,
            'name': group.name
        }

    def delete(self, group_id):
        """DELETE /api/groups/:id - Deletes a group"""
        group = Group.query.get_or_404(group_id)
        
        # Check if group has any words
        if group.words:
            return {
                'error': 'Cannot delete group that has words'
            }, 400
        
        db.session.delete(group)
        db.session.commit()
        
        return '', 204 