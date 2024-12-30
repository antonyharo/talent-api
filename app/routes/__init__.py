from app.routes.cv_routes import cv_bp
# from app.routes.jobs_routes import jobs_bp


def register_routes(app):
    app.register_blueprint(cv_bp, url_prefix="/cv")
    # app.register_blueprint(jobs_bp, url_prefix="/jobs")
