import json
import urllib.parse
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

class DatabaseConfig:
    """
    Класс для загрузки конфигурации подключения к БД из JSON-файла
    и создания синхронного или асинхронного движка SQLAlchemy.
    """
    def __init__(self, config_path: str, is_local: bool = True):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)['database']
        self.is_local = is_local

    def _build_string(self, is_async: bool = False) -> str:
        server = self.config['server']
        port = self.config.get('port', 1433)  # по умолчанию 1433
        database = self.config['name']
        username = self.config['username']
        password = self.config['password']
        driver = self.config['driver']

        # Кодируем пароль на случай специальных символов
        encoded_password = urllib.parse.quote_plus(password)

        # Выбираем префикс в зависимости от типа подключения
        if is_async:
            driver_name = "mssql+aiomssql"
        else:
            driver_name = "mssql+pyodbc"

        # Формируем строку подключения
        if self.is_local:
            connection_string = (
                f"{driver_name}://localhost/{database}"
                f"?driver={urllib.parse.quote_plus(driver)}"
            )
        else:
            connection_string = (
                f"{driver_name}://{username}:{encoded_password}@{server}:{port}/{database}"
                f"?driver={urllib.parse.quote_plus(driver)}"
            )
        return connection_string

    def sync_engine(self, echo: bool = False) -> Engine:
        connection_string = self._build_string(is_async=False)
        engine = create_engine(connection_string, echo=echo, connect_args={'charset': ' cp1251'})
        return engine

    def async_engine(self, echo: bool = False) -> AsyncEngine:
        connection_string = self._build_string(is_async=True)
        engine = create_async_engine(connection_string, echo=echo)
        return engine


config = DatabaseConfig('config\\db_config.json', True)

SyncEngine = config.sync_engine(echo=False)
SessionLocal: sessionmaker = sessionmaker(bind=SyncEngine)

def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()