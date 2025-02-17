from flask import Flask, jsonify
from flask_restful import Api, Resource
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from internal.models.models import db
from config import Config
from internal.handlers.dashboard import LastStudySessionAPI, StudyProgressAPI, QuickStatsAPI
from internal.handlers.words import WordListAPI, WordAPI
from internal.handlers.groups import GroupListAPI, GroupAPI, GroupWordsAPI, GroupStudySessionsAPI
from internal.handlers.study_sessions import StudySessionListAPI, StudySessionAPI, StudySessionWordsAPI
from internal.handlers.activities import StudyActivityListAPI, StudyActivityAPI
from internal.handlers.word_reviews import WordReviewAPI, WordReviewListAPI, WordReviewSessionAPI
from internal.middleware.error_handler import register_error_handlers
from internal.handlers.reset import ResetHistory, FullReset

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    api = Api(app)

    # Register error handlers
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    # Register API resources
    api.add_resource(LastStudySessionAPI, '/api/dashboard/last_study_session')
    api.add_resource(StudyProgressAPI, '/api/dashboard/study_progress')
    api.add_resource(QuickStatsAPI, '/api/dashboard/quick_stats')
    api.add_resource(ResetHistory, '/api/reset_history')  # Add this line
    api.add_resource(FullReset, '/api/full_reset')       # Add this line

    api.add_resource(WordListAPI, '/api/words')
    api.add_resource(WordAPI, '/api/words/<int:word_id>')

    api.add_resource(GroupListAPI, '/api/groups')
    api.add_resource(GroupAPI, '/api/groups/<int:group_id>')
    api.add_resource(GroupWordsAPI, '/api/groups/<int:group_id>/words')
    api.add_resource(GroupStudySessionsAPI, '/api/groups/<int:group_id>/study_sessions')  # Add this line

    api.add_resource(StudySessionListAPI, '/api/study_sessions')
    api.add_resource(StudySessionAPI, '/api/study_sessions/<int:session_id>')
    api.add_resource(StudySessionWordsAPI, '/api/study_sessions/<int:session_id>/words')

    api.add_resource(StudyActivityListAPI, '/api/study_activities')
    api.add_resource(StudyActivityAPI, '/api/study_activities/<int:activity_id>')

    api.add_resource(WordReviewListAPI, '/api/word_reviews')
    api.add_resource(WordReviewAPI, '/api/word_reviews/<int:review_id>')
    api.add_resource(WordReviewSessionAPI, '/api/study_sessions/<int:session_id>/words/<int:word_id>/review')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200

    # Debug routes endpoint (only enabled in debug mode)
    @app.route('/debug/routes')
    def list_routes():
        if not app.debug:
            return jsonify({'error': 'Only available in debug mode'}), 403
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        return jsonify({'routes': routes})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)