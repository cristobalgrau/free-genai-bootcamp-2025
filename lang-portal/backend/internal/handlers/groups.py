from flask import jsonify
from flask_restful import Resource
from internal.models.models import db, Group, Word, WordReviewItem
from sqlalchemy import func, case, text

class GroupListAPI(Resource):
    def get(self):
        """GET /api/groups - Returns all groups with word counts"""
        page = 1  # TODO: Get from request
        per_page = 100
        
        # Query groups with their word counts
        groups = db.session.query(
            Group,
            func.count(Word.id).label('word_count')
        ).outerjoin(Group.words)\
         .group_by(Group.id)\
         .paginate(page=page, per_page=per_page)
        
        return {
            'items': [{
                'id': group.Group.id,
                'name': group.Group.name,
                'word_count': group.word_count
            } for group in groups.items],
            'pagination': {
                'current_page': groups.page,
                'total_pages': groups.pages,
                'total_items': groups.total,
                'items_per_page': per_page
            }
        }

class GroupAPI(Resource):
    def get(self, group_id):
        """GET /api/groups/:id - Returns information about a specific group"""
        group = Group.query.get_or_404(group_id)
        
        # Get total word count
        word_count = db.session.query(func.count(Word.id))\
            .join(Word.groups)\
            .filter(Group.id == group_id)\
            .scalar()
        
        return {
            'id': group.id,
            'name': group.name,
            'stats': {
                'total_word_count': word_count
            }
        }

class GroupWordsAPI(Resource):
    def get(self, group_id):
        """GET /api/groups/:id/words - Returns all words in a group"""
        try:
            # Debug: Print group_id being requested
            print(f"Requesting words for group_id: {group_id}")
            
            # First verify group exists
            group = db.session.execute(
                text("SELECT id FROM groups WHERE id = :id"),
                {"id": group_id}
            ).fetchone()
            
            if not group:
                return {"error": "Group not found"}, 404

            # Debug: Print SQL query
            query = """
                SELECT 
                    w.id,
                    w.kanji,
                    w.romaji,
                    w.english,
                    w.parts,
                    COUNT(CASE WHEN wri.correct = 1 THEN 1 END) as correct_count,
                    COUNT(CASE WHEN wri.correct = 0 THEN 1 END) as wrong_count
                FROM words w
                INNER JOIN words_groups wg ON w.id = wg.word_id
                LEFT JOIN word_review_items wri ON w.id = wri.word_id
                WHERE wg.group_id = :group_id
                GROUP BY w.id, w.kanji, w.romaji, w.english, w.parts
            """
            print(f"Executing query:\n{query}")
            
            words = db.session.execute(
                text(query),
                {"group_id": group_id}
            ).fetchall()
            
            # Debug: Print results
            print(f"Found {len(words)} words")

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
                "total": len(words)
            }
            
        except Exception as e:
            print(f"Error in GroupWordsAPI: {str(e)}")
            # Return the actual error for debugging
            return {"error": str(e)}, 500

class GroupStudySessionsAPI(Resource):
    def get(self, group_id):
        """GET /api/groups/:id/study_sessions - Returns all study sessions for a group"""
        try:
            # First verify group exists
            group = db.session.execute(
                text("SELECT id FROM groups WHERE id = :id"),
                {"id": group_id}
            ).fetchone()
            
            if not group:
                return {"error": "Group not found"}, 404

            # Get study sessions for group
            sessions = db.session.execute(
                text("""
                    SELECT 
                        ss.id,
                        ss.created_at,
                        sa.name as activity_name,
                        COUNT(wri.id) as total_reviews,
                        SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END) as correct_reviews
                    FROM study_sessions ss
                    LEFT JOIN study_activities sa ON ss.study_activity_id = sa.id
                    LEFT JOIN word_review_items wri ON ss.id = wri.study_session_id
                    WHERE ss.group_id = :group_id
                    GROUP BY ss.id, ss.created_at, sa.name
                    ORDER BY ss.created_at DESC
                """),
                {"group_id": group_id}
            ).fetchall()

            return {
                "items": [{
                    "id": session[0],
                    "created_at": session[1],
                    "activity_name": session[2],
                    "total_reviews": session[3] or 0,
                    "correct_reviews": session[4] or 0
                } for session in sessions],
                "total": len(sessions)
            }
            
        except Exception as e:
            print(f"Error in GroupStudySessionsAPI: {str(e)}")
            return {"error": str(e)}, 500