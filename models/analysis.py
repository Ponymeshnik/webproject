from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from models_user import db, User  # предполагается, что db уже инициализирован там

# Проверяем, что у модели User есть поле is_premium (для обратной совместимости)
if not hasattr(User, 'is_premium'):
    if not hasattr(User, '__table__'):
        raise Exception("User model must be defined with SQLAlchemy Base")
    from sqlalchemy import Boolean
    User.is_premium = db.Column(Boolean, default=False)

# Модель для хранения истории анализов изображений
class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор анализа
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # ID пользователя
    image_filename = db.Column(db.String(256), nullable=False)  # Имя файла изображения
    metric_data = db.Column(db.Text, nullable=False)  # Метрики анализа (JSON в виде строки)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время анализа

    # Связь с пользователем
    user = db.relationship('User', backref=db.backref('analyses', lazy=True))
