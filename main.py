import logging
import sys
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import config
from handlers.commands import (
    start_command, stop_command, stats_command, 
    rules_command, help_command
)
from handlers.dice_handler import handle_dice_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    logger.info(f"Получен сигнал {signum}, завершаем работу...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("stop", stop_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("rules", rules_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", help_command))
        
        application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice_message))
        
        logger.info("🎰 БОТ ДЛЯ ТУРНИРОВ 777 ЗАПУЩЕН!")
        logger.info(f"👑 ID администратора: {config.ADMIN_ID}")
        logger.info("⏳ Ожидание сообщений...")
        
        application.run_polling(
            drop_pending_updates=True  # Только этот параметр
        )
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
