import logging
import sys
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Импортируем наши модули
from config import config
from handlers.commands import (
    start_command, stop_command, stats_command, 
    rules_command, help_command
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

async def post_init(application: Application):
    """Функция, выполняемая после инициализации бота"""
    logger.info("=" * 50)
    logger.info("🎰 БОТ ДЛЯ ТУРНИРОВ 777 ЗАПУЩЕН!")
    logger.info(f"👑 ID администратора: {config.ADMIN_ID}")
    logger.info(f"📊 Максимальная длительность турнира: {config.MAX_TOURNAMENT_DURATION} мин")
    logger.info(f"⏰ Лимит сообщений: {config.MESSAGE_AGE_LIMIT} сек")
    logger.info("=" * 50)
    logger.info("⏳ Ожидание сообщений...")

async def post_stop(application: Application):
    """Функция, выполняемая при остановке бота"""
    logger.info("🛑 Бот останавливается...")
    
    # Можно сохранить данные перед выходом
    from database import tournament_manager
    tournament_manager.save_to_file()

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
        
        # Добавляем обработчик эмодзи 🎰
        application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice_message))
        
        # Настраиваем обработчики событий
        application.post_init = post_init
        application.post_stop = post_stop
        
        # Запускаем бота
        logger.info("🚀 Запуск бота...")
        application.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
