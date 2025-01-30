from app.routes.hello_world_routes import hello_world_bp
from app.routes.cv_analyzer_routes import cv_analyzer_bp
from app.routes.jobs_routes import jobs_bp
from app.routes.ask_gemini_routes import ask_gemini_bp
from app.routes.jobs_comparator_routes import jobs_comparator_bp
from app.routes.best_profile_routes import best_profile_bp 


def register_routes(app):
    app.register_blueprint(hello_world_bp, url_prefix="/")
    app.register_blueprint(cv_analyzer_bp, url_prefix="/cv-analyzer")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(ask_gemini_bp, url_prefix="/gemini")
    app.register_blueprint(jobs_comparator_bp, url_prefix="/jobs-comparator")
    app.register_blueprint(best_profile_bp, url_prefix="/best-profile")
