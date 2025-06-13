from config_and_auth import app, db
from flask_migrate import Migrate

# Инициализация миграций базы данных
migrate = Migrate(app, db)

if __name__ == '__main__':
    # Запуск менеджера команд
    manager.run()