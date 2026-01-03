from flask import Flask
from backend.extensions import db, login_manager, bcrypt
from backend.models import User
from backend.auth import auth
from backend.routes import routes
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Logging Configuration
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register Blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(routes)
    
    with app.app_context():
        db.create_all()
        # Ensure default admin if needed logic here or manually via register
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
