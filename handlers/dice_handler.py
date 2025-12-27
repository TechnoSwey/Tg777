from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import asyncio

from config import config
from database import tournament_manager

class DiceChecker:
    """Проверка эмодзи 🎰 и сообщений"""
    
    @staticmethod
    def is_777(dice_emoji: str, dice_value: int) -> bool:
        """Проверяет, выпало ли 777"""
        return dice_emoji == "🎰" and dice_value == 64
    
    @staticmethod
    def is_forwarded_or_old_message(message) -> tuple[bool, str]:
        """Проверяет, является ли сообщение пересланным или старым"""
        
        # Проверяем признаки пересылки Telegram
        if hasattr(message, 'forward_from') and message.forward_from:
            return True, "Переслано от другого пользователя"
        
        if hasattr(message, 'forward_from_chat') and message.forward_from_chat:
            return True, "Переслано из другого чата"
        
        if hasattr(message, 'forward_from_message_id') and message.forward_from_message_id:
            return True, "Имеет ID оригинала"
        
        if hasattr(message, 'forward_sender_name') and message.forward_sender_name:
            return True, "Имя отправителя скрыто"
        
        if hasattr(message, 'forward_date') and message.forward_date:
            return True, "Имеет дату оригинала"
        
        # Проверяем возраст сообщения
        if hasattr(message, 'date'):
            message_time = message.date
            current_time = datetime.now(message_time.tzinfo)
            age_seconds = (current_time - message_time).total_seconds()
            
            if age_seconds > config.MESSAGE_AGE_LIMIT:
                return True, f"Сообщение старое ({int(age_seconds/60)} минут назад)"
        
        return False, "Оригинальное сообщение"

async def handle_dice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений с эмодзи 🎰"""
    
    # ========== ПРОВЕРКА АКТИВНОСТИ БОТА ==========
    if not config.BOT_ACTIVE:
        return  # БОТ ВЫКЛЮЧЕН - ВЫХОДИМ
    # ==============================================
    
    try:
        message = update.message
        
        # Проверяем, не является ли сообщение пересланным или старым
        is_invalid, reason = DiceChecker.is_forwarded_or_old_message(message)
        
        if is_invalid:
            # Если это 777, но сообщение невалидное - отправляем предупреждение
            if hasattr(message, 'dice') and message.dice:
                if DiceChecker.is_777(message.dice.emoji, message.dice.value):
                    warning = await message.reply_text(
                        f"⚠️ {message.from_user.mention_html()}, это сообщение не учитывается!\n"
                        f"Причина: {reason}\n\n"
                        f"📌 Отправьте новый 🎰 для участия!",
                        parse_mode=ParseMode.HTML
                    )
                    
                    # Удаляем предупреждение через 15 секунд
                    await asyncio.sleep(15)
                    try:
                        await warning.delete()
                    except:
                        pass
            
            return
        
        # Проверяем, что это эмодзи 🎰
        dice = message.dice
        if not dice or dice.emoji != "🎰":
            return
        
        user = message.from_user
        chat = message.chat
        
        # Проверяем, выпало ли 777
        if DiceChecker.is_777(dice.emoji, dice.value):
            
            # Турнирный режим
            if tournament_manager.is_tournament_active(chat.id):
                # Добавляем победу
                tournament_manager.add_win(chat.id, user.id, user.first_name)
                
                # Получаем текущий счет
                stats = tournament_manager.get_stats(chat.id)
                current_score = next((score for uid, score in stats if uid == user.id), 0)
                
                # Отправляем поздравление
                await message.reply_text(
                    f"🎉 **ДЖЕКПОТ!** 🎉\n\n"
                    f"Поздравляем, {user.mention_html()}! 🎰\n\n"
                    f"✅ **Засчитано в турнире!**\n"
                    f"📊 Текущий счет: {current_score} 🎰\n\n"
                    f"Продолжайте в том же духе!",
                    parse_mode=ParseMode.HTML
                )
            
            else:
                # Обычный режим (без турнира)
                congrats_message = await message.reply_text(
                    f"🎉 **ДЖЕКПОТ!** 🎉\n\n"
                    f"Поздравляем, {user.mention_html()}! 🎰\n\n"
                    f"💰 **ВЫИГРЫШ!** 💰\n\n"
                    f"Администратор свяжется с вами для получения награды!",
                    parse_mode=ParseMode.HTML
                )
                
                # Уведомляем админа
                await notify_admin_about_win(context, user, chat, congrats_message)
    
    except Exception as e:
        print(f"Ошибка обработки эмодзи: {e}")

async def notify_admin_about_win(context, user, chat, congrats_message):
    """Уведомляет администратора о выигрыше"""
    try:
        # Создаем ссылку на сообщение
        if chat.username:
            message_link = f"https://t.me/{chat.username}/{congrats_message.message_id}"
        else:
            chat_id_str = str(chat.id).replace('-100', '')
            message_link = f"https://t.me/c/{chat_id_str}/{congrats_message.message_id}"
        
        # Формируем сообщение админу
        admin_message = (
            f"🎰 **ВЫПАЛ ДЖЕКПОТ!** 🎰\n\n"
            f"👤 **Игрок:** {user.mention_html()}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📛 Имя: {user.first_name}\n"
            f"📝 Юзернейм: @{user.username if user.username else 'нет'}\n\n"
            f"💬 **Чат:** {chat.title if hasattr(chat, 'title') else 'Личный'}\n"
            f"🔗 **Ссылка:** {message_link}\n"
            f"⏰ **Время:** {congrats_message.date.strftime('%H:%M:%S')}"
        )
        
        # Создаем кнопки
        keyboard = [
            [
                InlineKeyboardButton("📨 Написать игроку", 
                                   url=f"tg://user?id={user.id}"),
                InlineKeyboardButton("🔗 Перейти к сообщению", 
                                   url=message_link)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем админу
        await context.bot.send_message(
            chat_id=config.ADMIN_ID,
            text=admin_message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"Ошибка уведомления админа: {e}")
