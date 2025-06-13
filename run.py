from config_and_auth import app
from models_user import db
from flask import session, g
from models_user import User
# Импортируем все маршруты
import auth_routes
import frontend_routes
from api.emotion_api import emotion_api
app.register_blueprint(emotion_api)
# Перед каждым запросом загружаем пользователя в g (необязательно, если используете Flask-Login)
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id:
        g.user = User.query.get(user_id)
    else:
        g.user = None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
