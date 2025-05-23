
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config        # 原来是  from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes.user_routes import bp as user_bp
    from .routes.session_routes import bp as session_bp
    from .routes.rppg_routes import bp as rppg_bp
    from .routes.twin_routes import bp as twin_bp
    from .routes.tips_routes import bp as tips_bp
    from .routes.health_routes import bp as health_bp
    #二期
    from .routes.friend_routes import bp as friend_bp
    from .routes.challenge_routes import bp as challenge_bp
    #三期
    from .routes.post_routes import bp as post_bp
    from .routes.notify_routes import bp as notify_bp

    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(session_bp, url_prefix='/api/session')
    app.register_blueprint(rppg_bp, url_prefix='/api/rppg')
    app.register_blueprint(twin_bp, url_prefix='/api/twin')
    app.register_blueprint(tips_bp, url_prefix='/api/tips')
    app.register_blueprint(health_bp, url_prefix='/api')
    # 二期
    app.register_blueprint(friend_bp, url_prefix='/api/friend')
    app.register_blueprint(challenge_bp, url_prefix='/api/challenge')
    #三期
    app.register_blueprint(post_bp)
    app.register_blueprint(notify_bp)



    return app
