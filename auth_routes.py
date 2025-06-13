from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from functools import wraps
from flask import abort
from datetime import date, datetime

from models_user import db, User
from config_and_auth import app

# Маршрут для регистрации нового пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Проверка на уникальность логина и email
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Пользователь с таким логином или email уже существует.')
            return redirect(url_for('register'))

        # Создание нового пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Войдите в аккаунт.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Маршрут для входа пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form['username']
        password = request.form['password']

        # Проверяем пользователя
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # Вход через Flask-Login
            flash('Успешный вход!')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль.')

    return render_template('login.html')

# Временный маршрут для назначения премиум-статуса пользователю (для тестирования)
@app.route('/make_premium/<username>')
def make_premium(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_premium = True
        db.session.commit()
        return f"{username} теперь премиум!"
    return "Пользователь не найден"

# Временный маршрут для назначения статуса администратора пользователю (для тестирования)
@app.route('/make_admin/<username>')
def make_admin(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_admin = True
        db.session.commit()
        return f"{username} теперь админ!"
    return "Пользователь не найден"

# Маршрут для выхода пользователя
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('index'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.all()
    from models.analysis import AnalysisHistory
    today = date.today()
    user_limits = {}
    for u in users:
        if u.is_premium:
            user_limits[u.id] = "∞"
        else:
            used = AnalysisHistory.query.filter(
                AnalysisHistory.user_id == u.id,
                AnalysisHistory.timestamp >= datetime.combine(today, datetime.min.time())
            ).count()
            user_limits[u.id] = f"{used}/10"
    return render_template('admin.html', users=users, user_limits=user_limits)

@app.route('/admin/make_premium/<int:user_id>', methods=['POST'])
@admin_required
def admin_make_premium(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_premium = True
        db.session.commit()
        flash(f"{user.username} теперь премиум!")
    return redirect(url_for('admin_panel'))

@app.route('/admin/make_admin/<int:user_id>', methods=['POST'])
@admin_required
def admin_make_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
        flash(f"{user.username} теперь админ!")
    return redirect(url_for('admin_panel'))

@app.route('/admin/reset_limit/<int:user_id>', methods=['POST'])
@admin_required
def admin_reset_limit(user_id):
    from models.analysis import AnalysisHistory
    # Удаляем все анализы пользователя за сегодня (или можно реализовать по-другому)
    today = date.today()
    AnalysisHistory.query.filter(
        AnalysisHistory.user_id == user_id,
        AnalysisHistory.timestamp >= datetime.combine(today, datetime.min.time())
    ).delete()
    db.session.commit()
    flash("Лимит сброшен!")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("Пользователь удалён!")
    return redirect(url_for('admin_panel'))

@app.route('/admin/remove_premium/<int:user_id>', methods=['POST'])
@admin_required
def admin_remove_premium(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_premium = False
        db.session.commit()
        flash(f"{user.username} больше не премиум.")
    return redirect(url_for('admin_panel'))

@app.route('/admin/remove_admin/<int:user_id>', methods=['POST'])
@admin_required
def admin_remove_admin(user_id):
    user = User.query.get(user_id)
    if user and user.id != current_user.id:
        user.is_admin = False
        db.session.commit()
        flash(f"{user.username} больше не админ.")
    elif user and user.id == current_user.id:
        flash("Нельзя снять админку с самого себя!")
    return redirect(url_for('admin_panel'))
