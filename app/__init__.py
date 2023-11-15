from flask import Flask
from flask_cors import CORS

from .routes import api_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.url_map.strict_slashes = False  # ignore tailing slash

    @app.errorhandler(404)
    def page_not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        print(error)
        return {
            "error": "Internal Server Error",
            "message": str(error),
        }, 500

    @app.route("/ping")
    def ping():
        return "pong"

    app.register_blueprint(api_bp, url_prefix="/api")
    return app
