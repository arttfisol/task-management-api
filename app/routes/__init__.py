from flask import Blueprint
from app.routes.task import task_bp

api_bp = Blueprint("index", __name__)

api_bp.register_blueprint(task_bp, url_prefix="/tasks")
