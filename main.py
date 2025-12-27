#!/usr/bin/env python3
"""
🎰 Telegram бот для турниров по эмодзи 777
Запуск: python main.py
"""

import logging
import sys
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Импортируем наши модули
from config import config
from handlers.commands import (
    start_command, stop_command, stats_command, 
    rules_command, help_command, active_command, inactive_command
)
from handlers.dice_handler import handle_dice_message

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Уменьшаем логирование библиотек
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Получен сигнал {signum}, завершаем работу...")
    sys.exit(0)

def main():
    """Основная функция запуска бота"""
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Создаем приложение
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("stop", stop_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("rules", rules_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", help_command))
        
        # Добавляем новые команды для активации/деактивации
        application.add_handler(CommandHandler("active", active_command))
        application.add_handler(CommandHandler("inactive", inactive_command))
        
        # Добавляем обработчик эмодзи 🎰
        application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice_message))
        
        # Запускаем бота
        logger.info("🎰 БОТ ДЛЯ ТУРНИРОВ 777 ЗАПУЩЕН!")
        logger.info(f"👑 ID администратора: {config.ADMIN_ID}")
        logger.info(f"📊 Максимальная длительность турнира: {config.MAX_TOURNAMENT_DURATION} мин")
        logger.info(f"⏰ Лимит сообщений: {config.MESSAGE_AGE_LIMIT} сек")
        logger.info(f"🔌 Статус бота: {'АКТИВЕН' if config.BOT_ACTIVE else 'ВЫКЛЮЧЕН'}")
        logger.info("⏳ Ожидание сообщений...")
        
        # Упрощенный запуск
        application.run_polling(
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
