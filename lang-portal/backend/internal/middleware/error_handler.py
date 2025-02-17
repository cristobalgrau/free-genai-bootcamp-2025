from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        return jsonify({'error': 'Database error occurred'}), 500

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({'error': error.description}), error.code