from flask_restful import Resource
from internal.models.models import db
from sqlalchemy import text

class ResetHistory(Resource):
    def post(self):
        try:
            # Execute each statement separately
            db.session.execute(text("DELETE FROM word_review_items"))
            db.session.execute(text("DELETE FROM study_sessions"))
            db.session.commit()
            
            return {
                "success": True,
                "message": "Study history has been reset"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class FullReset(Resource):
    def post(self):
        try:
            # Execute each statement separately
            db.session.execute(text("DELETE FROM word_review_items"))
            db.session.execute(text("DELETE FROM study_sessions"))
            db.session.execute(text("DELETE FROM study_activities"))
            db.session.execute(text("DELETE FROM words_groups"))
            db.session.commit()
            
            return {
                "success": True,
                "message": "System has been fully reset"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500