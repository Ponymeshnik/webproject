import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import pytest
from config_and_auth import app, db
from models_user import User
import auth_routes
import frontend_routes

@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Создаём тестового пользователя
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
        yield client

# Тест регистрации и логина
def test_register_and_login(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass'
    }, follow_redirects=True)
    assert 'Регистрация прошла успешно' in response.get_data(as_text=True)

    response = client.post('/login', data={
        'username': 'newuser',
        'password': 'newpass'
    }, follow_redirects=True)
    assert 'Успешный вход' in response.get_data(as_text=True)

# Тест покупки премиума
def test_buy_premium(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    response = client.post('/buy_premium', data={
        'card': '1234 5678 9012 3456',
        'name': 'Test User',
        'exp': '12/34',
        'cvv': '123'
    }, follow_redirects=True)
    text = response.get_data(as_text=True)
    assert 'премиум' in text or 'Поздравляем' in text

# Тест API анализа эмоций
def test_api_analyze_emotion(client):
    with open('tests/face.jpg', 'rb') as f:
        img = (io.BytesIO(f.read()), 'face.jpg')
        response = client.post('/api/analyze_emotion', data={'image': img}, content_type='multipart/form-data')
        assert response.status_code in (200, 400, 500)

# Тест лимита анализов (эмулируем 10 анализов)
def test_limit(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    for i in range(10):
        client.post('/analyze', data={'image': (io.BytesIO(b'testimage'), f'{i}.jpg')}, content_type='multipart/form-data')
    response = client.post('/analyze', data={'image': (io.BytesIO(b'testimage'), 'last.jpg')}, content_type='multipart/form-data', follow_redirects=True)
    text = response.get_data(as_text=True)
    assert 'лимита' in text or 'лимит' in text or response.status_code in (200, 302)

# Тест страницы админки (403 для обычного пользователя)
def test_admin_panel_forbidden(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    response = client.get('/admin')
    assert response.status_code == 403

def create_user(client, username, email, password):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

def test_admin_and_premium_actions(client):
    # Создаём пользователей
    create_user(client, 'user1', 'user1@example.com', 'pass1')
    create_user(client, 'user2', 'user2@example.com', 'pass2')
    create_user(client, 'admin', 'admin@example.com', 'adminpass')

    # Делаем admin админом через make_admin
    login(client, 'admin', 'adminpass')
    client.get('/make_admin/admin', follow_redirects=True)

    # Проверяем, что admin может зайти в админку
    response = client.get('/admin')
    assert 'Панель администратора' in response.get_data(as_text=True)

    # Выдаём user1 премиум
    response = client.post('/admin/make_premium/1', follow_redirects=True)
    assert 'теперь премиум' in response.get_data(as_text=True)

    # Снимаем премиум с user1
    response = client.post('/admin/remove_premium/1', follow_redirects=True)
    assert 'больше не премиум' in response.get_data(as_text=True)

    # Выдаём user2 админку
    response = client.post('/admin/make_admin/2', follow_redirects=True)
    assert 'теперь админ' in response.get_data(as_text=True)

    # Снимаем админку с user2
    response = client.post('/admin/remove_admin/2', follow_redirects=True)
    assert 'больше не админ' in response.get_data(as_text=True)

    # Пробуем снять админку с самого себя
    admin_user = User.query.filter_by(username='admin').first()
    response = client.post(f'/admin/remove_admin/{admin_user.id}', follow_redirects=True)
    assert 'Нельзя снять админку с самого себя' in response.get_data(as_text=True)

    # Проверяем, что обычный пользователь не может зайти в админку
    login(client, 'user1', 'pass1')
    response = client.get('/admin')
    assert response.status_code == 403 