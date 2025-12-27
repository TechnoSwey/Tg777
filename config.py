import os
import sys
from typing import Optional

class Config:
    """Класс для управления конфигурацией бота"""
    
    def __init__(self):
        # Получаем токен бота из переменных окружения
        self.BOT_TOKEN = self._get_env_var('BOT_TOKEN')
        
        # ID администратора
        self.ADMIN_ID = int(self._get_env_var('ADMIN_ID', '0'))

        self.BOT_ACTIVE = True
        
        # Настройки турнира
        self.MAX_TOURNAMENT_DURATION = 1440  # Максимум 24 часа в минутах
        self.MESSAGE_AGE_LIMIT = 120  # 2 минуты в секундах
        
        # Настройки логирования
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = 'bot.log'
        
        # Проверяем обязательные переменные
        self._validate_config()
    
    def _get_env_var(self, var_name: str, default: Optional[str] = None) -> str:
        """Получает переменную окружения с проверкой"""
        value = os.getenv(var_name, default)
        
        if var_name == 'BOT_TOKEN' and (not value or value == 'YOUR_BOT_TOKEN_HERE'):
            print(f"❌ ОШИБКА: {var_name} не установлен!")
            print("Создайте бота через @BotFather и установите токен:")
            print("export BOT_TOKEN='ваш_токен_бота'")
            sys.exit(1)
        
        return value
    
    def _validate_config(self):
        """Проверяет конфигурацию"""
        if self.ADMIN_ID == 0:
            print("⚠️ ВНИМАНИЕ: ADMIN_ID не установлен. Админские функции отключены.")
            print("Получите ваш ID через @userinfobot и установите:")
            print("export ADMIN_ID='ваш_id'")

# Создаем глобальный объект конфигурации
config = Config()
