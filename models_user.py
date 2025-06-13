from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор пользователя
    username = db.Column(db.String(64), unique=True, nullable=False)  # Имя пользователя
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email пользователя
    password_hash = db.Column(db.String(128), nullable=False)  # Хэш пароля
    is_premium = db.Column(db.Boolean, default=False)  # Флаг премиум-статуса
    is_admin = db.Column(db.Boolean, default=False)  # Флаг администратора

    def set_password(self, password):
        """Устанавливает хэш пароля для пользователя."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль пользователя."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
