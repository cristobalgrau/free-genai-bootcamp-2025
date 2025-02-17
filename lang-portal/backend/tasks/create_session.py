from internal.models.models import db
from sqlalchemy import text
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def create_session(app):
    """Create a study session with app context"""
    with app.app_context():
        try:
            # Debug: Check groups using raw SQL
            groups = db.session.execute(text("SELECT * FROM groups;")).fetchall()
            print("\nGroups in database:")
            for group in groups:
                print(f"  ID: {group[0]}, Name: {group[1]}")
            
            # Debug: Check activities using raw SQL
            activities = db.session.execute(text("SELECT id, name, thumbnail_url FROM study_activities;")).fetchall()
            print("\nActivities in database:")
            for activity in activities:
                print(f"  ID: {activity[0]}, Name: {activity[1]}, Thumbnail: {activity[2]}")
            
            # Get first group and activity
            group_id = db.session.execute(text("SELECT id FROM groups LIMIT 1;")).scalar()
            activity_id = db.session.execute(text("SELECT id FROM study_activities LIMIT 1;")).scalar()
            
            print(f"\nSelected group_id: {group_id}")
            print(f"Selected activity_id: {activity_id}")
            
            if group_id and activity_id:
                # Create study session with explicit values in a single transaction
                session_result = db.session.execute(
                    text("""
                        INSERT INTO study_sessions (group_id, created_at, study_activity_id)
                        VALUES (:group_id, datetime('now'), :activity_id)
                        RETURNING id;
                    """),
                    {"group_id": group_id, "activity_id": activity_id}
                )
                session_id = session_result.scalar()
                
                # Create word reviews
                db.session.execute(
                    text("""
                        INSERT INTO word_review_items (word_id, study_session_id, correct, created_at)
                        SELECT id, :session_id, true, datetime('now')
                        FROM words
                        LIMIT 2;
                    """),
                    {"session_id": session_id}
                )
                
                # Commit all changes in one go
                db.session.commit()
                
                print(f"\nStudy session created successfully:")
                print(f"  Session ID: {session_id}")
                print(f"  Group ID: {group_id}")
                print(f"  Activity ID: {activity_id}")
            else:
                print("\nNo groups or activities found")
                
        except Exception as e:
            print(f"\nError creating session: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    flask_app = create_app()
    create_session(flask_app)