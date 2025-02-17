from flask import jsonify, request
from flask_restful import Resource
from internal.models.models import db, Word, Group
from sqlalchemy import func
import json  # Add this import at the top of your file

class WordListAPI(Resource):
    def get(self):
        """GET /api/words - Returns all words with pagination"""
        page = 1  # TODO: Get from request
        per_page = 100
        
        words = db.session.query(Word).paginate(page=page, per_page=per_page)
        
        return {
            'items': [{
                'id': word.id,
                'japanese': word.japanese,
                'romaji': word.romaji,
                'english': word.english
            } for word in words.items],
            'pagination': {
                'current_page': words.page,
                'total_pages': words.pages,
                'total_items': words.total,
                'items_per_page': per_page
            }
        }

    def post(self):
        """POST /api/words - Creates a new word"""
        data = request.get_json()
        
        if not data or 'japanese' not in data or 'romaji' not in data or 'english' not in data:
            return {'error': 'Japanese, Romaji, and English fields are required'}, 400
            
        # Convert parts to JSON string if it exists
        parts = json.dumps(data.get('parts')) if 'parts' in data else None
        
        word = Word(
            japanese=data['japanese'],
            romaji=data['romaji'],
            english=data['english'],
            parts=parts  # Store as JSON string
        )
        
        db.session.add(word)
        db.session.commit()
        
        return {
            'id': word.id,
            'japanese': word.japanese,
            'romaji': word.romaji,
            'english': word.english
        }, 201

class WordAPI(Resource):
    def get(self, word_id):
        """GET /api/words/:id - Returns details about a specific word"""
        word = Word.query.get_or_404(word_id)
        
        return {
            'id': word.id,
            'japanese': word.japanese,
            'romaji': word.romaji,
            'english': word.english,
            'parts': word.parts
        }

    def put(self, word_id):
        """PUT /api/words/:id - Updates a word"""
        word = Word.query.get_or_404(word_id)
        data = request.get_json()
        
        if not data:
            return {'error': 'No data provided'}, 400
            
        word.japanese = data.get('japanese', word.japanese)
        word.romaji = data.get('romaji', word.romaji)
        word.english = data.get('english', word.english)
        word.parts = data.get('parts', word.parts)
        
        db.session.commit()
        
        return {
            'id': word.id,
            'japanese': word.japanese,
            'romaji': word.romaji,
            'english': word.english,
            'parts': word.parts
        }

    def delete(self, word_id):
        """DELETE /api/words/:id - Deletes a word"""
        word = Word.query.get_or_404(word_id)
        
        db.session.delete(word)
        db.session.commit()
        
        return '', 204 