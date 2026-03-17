import os
from flask import Flask
from dotenv import load_dotenv
from backend.db import db
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

load_dotenv()

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
@app.route("/")
def home():
    return """
    <h1>LinkHub Pro 🚀</h1>
    <p><a href='/register'>Register</a></p>
    <p><a href='/login'>Login</a></p>
    """
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
from backend.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# Import routes
from backend.routes.auth import auth_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.public import public_bp
from backend.routes.analytics import analytics_bp
app.register_blueprint(analytics_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(public_bp)

if __name__ == "__main__":
    app.run(debug=True)
