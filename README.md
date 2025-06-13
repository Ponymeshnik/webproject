# Emotion Detection Web App

Это веб-приложение на Flask использует предобученную модель из библиотеки DeepFace для анализа эмоций по фотографии лица.

## 🚀 Возможности
- REST API `/api/analyze_emotion` принимает изображение и возвращает JSON с эмоцией.
- Поддержка популярных эмоций: `happy`, `sad`, `angry`, `surprise`, `fear`, `neutral` и др.

## 🧠 Используемые технологии
- Python 3.10+
- Flask
- DeepFace
- OpenCV, Pillow
- Pytest для тестирования

## 📦 Установка
```bash
git clone https://github.com/yourusername/emotion-detector.git
cd emotion-detector
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

## 🔄 Запуск приложения
```bash
python app.py
```
Приложение будет доступно по адресу: `http://127.0.0.1:5000`

## 📤 Пример запроса к API
```bash
curl -X POST -F "image=@face.jpg" http://127.0.0.1:5000/api/analyze_emotion
```

Пример ответа:
```json
{
  "dominant_emotion": "happy",
  "emotion_scores": {
    "angry": 0.01,
    "disgust": 0.0,
    "fear": 0.02,
    "happy": 0.92,
    "sad": 0.03,
    "surprise": 0.01,
    "neutral": 0.01
  }
}
```

## ✅ Тестирование
```bash
pytest
```

## 🧾 Лицензия
MIT
