import uuid
from datetime import datetime, date
from flask import request, session, redirect, url_for, flash, render_template
import requests
import json
import os

from flask_login import current_user

from models.analysis import AnalysisHistory
from models_user import db, User
from config_and_auth import app

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для анализа изображения
@app.route('/analyze', methods=['POST'])
def analyze():
    from deepface import DeepFace

    user = current_user if current_user.is_authenticated else None

    # Проверка лимита для обычных пользователей
    if user and not user.is_premium:
        today = date.today()
        count_today = AnalysisHistory.query.filter(
            AnalysisHistory.user_id == user.id,
            AnalysisHistory.timestamp >= datetime.combine(today, datetime.min.time())
        ).count()

        if count_today >= 10:
            flash("Вы достигли лимита анализов на сегодня (10). Попробуйте завтра или оформите премиум.")
            return redirect(url_for('history'))

    image = request.files['image']
    if image:
        filename = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
        image_path = os.path.join('static/uploads', filename)
        image.save(image_path)

        try:
            # Получаем метрики
            result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)[0]

            dominant = result.get('dominant_emotion', 'не определено')
            emotion_scores = result.get('emotion', {})

            # Формируем словарь метрик
            metrics = {
                "Основная эмоция": dominant,
            }
            for emotion, score in emotion_scores.items():
                metrics[emotion] = round(score, 2)

        except Exception as e:
            metrics = {"Ошибка": str(e)}
            flash(f"Ошибка анализа: {e}")

        # Сохраняем результат анализа в БД
        metric_json = json.dumps(metrics)
        new_analysis = AnalysisHistory(
            user_id=user.id if user else None,
            image_filename=filename,
            metric_data=metric_json
        )
        db.session.add(new_analysis)
        db.session.commit()

        flash("Анализ выполнен.")

        if user:
            return redirect(url_for('history'))
        else:
            return render_template('index.html', last_analysis={
                'image_url': url_for('static', filename='uploads/' + filename),
                'metrics': metrics
            })

    flash("Ошибка загрузки файла.")
    return redirect(url_for('index'))

# просмотр истории анализов пользователя
@app.route('/history')
def history():
    if not current_user.is_authenticated:
        flash("Войдите в аккаунт для просмотра истории.")
        return redirect(url_for('login'))

    # Получаем все анализы текущего пользователя
    analyses = AnalysisHistory.query.filter_by(user_id=current_user.id).order_by(AnalysisHistory.timestamp.desc()).all()

    # Преобразуем метрики из строки JSON в словарь для шаблона
    for a in analyses:
        a.metric_data_dict = json.loads(a.metric_data)

    # Информация о лимитах для отображения в шаблоне
    limit_info = None
    if current_user.is_authenticated and not current_user.is_premium:
        today = date.today()
        used = AnalysisHistory.query.filter(
            AnalysisHistory.user_id == current_user.id,
            AnalysisHistory.timestamp >= datetime.combine(today, datetime.min.time())
        ).count()
        remaining = max(0, 10 - used)
        limit_info = {
            "Тип аккаунта": "Обычный",
            "Осталось анализов на сегодня": remaining
        }
    elif current_user.is_authenticated:
        limit_info = {
            "Тип аккаунта": "Премиум",
            "Лимитов нет": "∞"
        }

    return render_template('history.html', analyses=analyses, limits=limit_info)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        flash("Войдите в аккаунт для просмотра профиля.")
        return redirect(url_for('login'))
    return render_template('profile.html', user=current_user)

@app.route('/buy_premium', methods=['GET', 'POST'])
def buy_premium():
    if not current_user.is_authenticated:
        flash("Войдите в аккаунт для покупки премиума.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        card = request.form.get('card')
        name = request.form.get('name')
        exp = request.form.get('exp')
        cvv = request.form.get('cvv')
        if not card or not name or not exp or not cvv or len(card.replace(' ', '')) != 16:
            flash("Проверьте правильность заполнения данных!")
            return render_template('buy_premium.html')
        # Делаем пользователя премиумом
        current_user.is_premium = True
        db.session.commit()
        flash("Поздравляем! Вы стали премиум-пользователем.")
        return redirect(url_for('profile'))
    return render_template('buy_premium.html')


