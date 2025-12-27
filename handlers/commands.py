from datetime import datetime
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import config
from database import tournament_manager

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Личный чат с ботом
    if chat.type == 'private':
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"🎰 Я бот для проведения турниров по эмодзи 777.\n\n"
            f"📋 **Как использовать:**\n"
            f"1. Добавьте меня в группу\n"
            f"2. Дайте права администратора\n"
            f"3. В группе напишите /start для начала турнира\n"
            f"4. Напишите /stop для завершения турнира\n\n"
            f"🏆 Во время турнира я считаю все выпавшие 777 🎰\n"
            f"📊 После /stop показываю статистику и определяю победителя!\n\n"
            f"👑 Админские команды работают только от администратора чата."
        )
        return
    
    # Групповой чат - проверяем админа
    if user.id != config.ADMIN_ID:
        await update.message.reply_text(
            "⛔ Эта команда только для администратора чата!",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Парсим аргументы (время турнира)
    duration = None
    if context.args:
        try:
            duration = int(context.args[0])
            if duration <= 0 or duration > config.MAX_TOURNAMENT_DURATION:
                await update.message.reply_text(
                    f"⏱️ Укажите длительность от 1 до {config.MAX_TOURNAMENT_DURATION} минут!\n"
                    f"Пример: /start 60 (турнир на 1 час)",
                    parse_mode=ParseMode.HTML
                )
                return
        except ValueError:
            await update.message.reply_text(
                "⚠️ Неверный формат времени! Используйте число минут.\n"
                "Пример: /start 60",
                parse_mode=ParseMode.HTML
            )
            return
    
    # Проверяем, не активен ли уже турнир
    if tournament_manager.is_tournament_active(chat.id):
        await update.message.reply_text(
            "⚠️ В этом чате уже идет турнир!\n"
            "Используйте /stop чтобы завершить текущий турнир.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Запускаем турнир
    success = tournament_manager.start_tournament(chat.id, chat.title, duration)
    
    if not success:
        await update.message.reply_text(
            "❌ Не удалось запустить турнир. Попробуйте снова.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Формируем сообщение о начале турнира
    duration_text = f"⏱️ **Длительность:** {duration} минут" if duration else "⏱️ **Без ограничения по времени**"
    
    rules_text = (
        "📋 **Правила:**\n"
        "✅ Учитываются только свежие сообщения\n"
        "❌ Пересланные 🎰 не засчитываются\n"
        "❌ Сообщения старше 2 минут игнорируются\n\n"
        "⚖️ **Только честная игра!**"
    )
    
    await update.message.reply_text(
        f"🎰 **ТУРНИР НАЧАЛСЯ!** 🎰\n\n"
        f"📊 Веду подсчет всех выпавших 777.\n"
        f"{duration_text}\n"
        f"🏆 Победит игрок с наибольшим количеством 777!\n\n"
        f"{rules_text}\n\n"
        f"**Команды:**\n"
        f"`/stop` - завершить турнир\n"
        f"`/stats` - текущая статистика\n"
        f"`/rules` - правила турнира",
        parse_mode=ParseMode.HTML
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Только в групповых чатах
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "Эта команда работает только в групповых чатах!",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Только для админа
    if user.id != config.ADMIN_ID:
        await update.message.reply_text(
            "⛔ Только администратор может завершить турнир!",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Останавливаем турнир
    results = tournament_manager.stop_tournament(chat.id)
    
    if not results:
        await update.message.reply_text(
            "📭 В этом чате нет активного турнира!\n"
            "Используйте /start чтобы начать новый турнир.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Отправляем результаты в чат
    await send_tournament_results(update, results, chat)
    
    # Отправляем детальный отчет админу
    await send_detailed_report_to_admin(context, results, chat)

async def send_tournament_results(update: Update, results: Dict, chat):
    """Отправляет результаты турнира в чат"""
    player_stats = results['player_stats']
    tournament_data = results['tournament_data']
    
    if not player_stats:
        await update.message.reply_text(
            "🎰 **ТУРНИР ОКОНЧЕН** 🎰\n\n"
            "😔 За время турнира не было выбито ни одной комбинации 777.\n\n"
            "📌 Помните: учитываются только свежие сообщения!\n\n"
            "Ждем вас в следующем турнире! 🎉",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Сортируем игроков
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1], reverse=True)
    
    # Формируем сообщение
    results_text = "🏁 **ТУРНИР ОКОНЧЕН!** 🏁\n\n"
    
    # Статистика турнира
    duration = tournament_data['end_time'] - tournament_data['start_time']
    hours, remainder = divmod(int(duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    results_text += f"📊 **Статистика турнира:**\n"
    results_text += f"• ⏱️ Длительность: {hours:02d}:{minutes:02d}:{seconds:02d}\n"
    results_text += f"• 👥 Участников: {len(sorted_players)}\n"
    results_text += f"• 🎰 Всего 777: {sum(player_stats.values())}\n\n"
    
    # Топ игроков
    results_text += "🏆 **ТОП ИГРОКОВ:** 🏆\n\n"
    
    for i, (user_id, wins) in enumerate(sorted_players[:10], 1):
        try:
            user_info = await update.message.bot.get_chat(user_id)
            username = f"@{user_info.username}" if user_info.username else user_info.first_name
            
            if i == 1:
                results_text += f"🥇 **{username}:** {wins} 🎰\n"
            elif i == 2:
                results_text += f"🥈 {username}: {wins} 🎰\n"
            elif i == 3:
                results_text += f"🥉 {username}: {wins} 🎰\n"
            else:
                results_text += f"{i}. {username}: {wins} 🎰\n"
        except Exception as e:
            results_text += f"{i}. ID{user_id}: {wins} 🎰\n"
    
    if len(sorted_players) > 10:
        results_text += f"\n... и еще {len(sorted_players) - 10} участников"
    
    results_text += "\n\n🎉 **Поздравляем победителей!** 🎉"
    
    await update.message.reply_text(results_text, parse_mode=ParseMode.HTML)

async def send_detailed_report_to_admin(context, results: Dict, chat):
    """Отправляет детальный отчет админу"""
    player_stats = results['player_stats']
    tournament_data = results['tournament_data']
    
    if not player_stats:
        return
    
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1], reverse=True)
    
    report = f"📊 **ОТЧЕТ О ТУРНИРЕ** 📊\n\n"
    report += f"💬 Чат: {tournament_data['chat_title']}\n"
    report += f"🆔 ID: `{chat.id}`\n\n"
    
    # Детальная статистика
    report += f"📈 **Детальная статистика:**\n"
    
    for i, (user_id, wins) in enumerate(sorted_players, 1):
        try:
            user_info = await context.bot.get_chat(user_id)
            username = f"@{user_info.username}" if user_info.username else user_info.first_name
            report += f"{i}. {username} (ID: `{user_id}`): {wins} 🎰\n"
        except:
            report += f"{i}. ID{user_id}: {wins} 🎰\n"
    
    await context.bot.send_message(
        chat_id=config.ADMIN_ID,
        text=report,
        parse_mode=ParseMode.HTML
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "Эта команда работает только в группах!",
            parse_mode=ParseMode.HTML
        )
        return
    
    if not tournament_manager.is_tournament_active(chat.id):
        await update.message.reply_text(
            "📭 В этом чате нет активного турнира!\n"
            "Используйте /start чтобы начать турнир.",
            parse_mode=ParseMode.HTML
        )
        return
    
    stats = tournament_manager.get_stats(chat.id)
    
    if not stats:
        await update.message.reply_text(
            "📊 **Текущая статистика:**\n\n"
            "Пока никто не выбил 777. Ждем первого победителя! 🎰",
            parse_mode=ParseMode.HTML
        )
        return
    
    stats_text = "📊 **ТЕКУЩАЯ СТАТИСТИКА ТУРНИРА** 📊\n\n"
    
    for i, (user_id, wins) in enumerate(stats[:10], 1):
        try:
            user_info = await context.bot.get_chat(user_id)
            username = f"@{user_info.username}" if user_info.username else user_info.first_name
            stats_text += f"{i}. {username}: {wins} 🎰\n"
        except:
            stats_text += f"{i}. ID{user_id}: {wins} 🎰\n"
    
    if len(stats) > 10:
        stats_text += f"\n... и еще {len(stats) - 10} участников"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /rules"""
    rules_text = (
        "📋 **ПРАВИЛА ТУРНИРА** 📋\n\n"
        
        "✅ **ЗАСЧИТЫВАЕТСЯ:**\n"
        "• Только новые сообщения с 🎰\n"
        "• Сообщения отправленные лично вами\n"
        "• Сообщения младше 2 минут\n\n"
        
        "❌ **НЕ ЗАСЧИТЫВАЕТСЯ:**\n"
        "• Пересланные сообщения (даже свои старые!)\n"
        "• Сообщения из истории чата\n"
        "• Сообщения старше 2 минут\n\n"
        
        "⚖️ **СИСТЕМА ЧЕСТНАЯ:**\n"
        "• Автоматическая проверка каждого сообщения\n"
        "• Определение пересланных сообщений\n"
        "• Проверка времени отправки\n\n"
        
        "🎯 **ВЕРОЯТНОСТЬ ВЫИГРЫША:** 1/64 ≈ 1.56%\n\n"
        
        "🏆 **ПОБЕДИТЕЛЬ:** Игрок с наибольшим количеством 777\n"
        "При равенстве очков - несколько победителей\n\n"
        
        "❓ **Вопросы?** Обращайтесь к администратору чата!"
    )
    
    await update.message.reply_text(rules_text, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "🎰 **Бот для турниров по эмодзи 777** 🎰\n\n"
        
        "👑 **Команды для администратора:**\n"
        "`/start [минуты]` - Начать турнир\n"
        "`/stop` - Завершить турнир и показать результаты\n"
        "`/stats` - Текущая статистика турнира\n"
        "`/rules` - Правила турнира\n\n"
        
        "📋 **Важные правила:**\n"
        "• Учитываются ТОЛЬКО свежие сообщения (<2 мин)\n"
        "• Пересланные 🎰 НЕ засчитываются\n"
        "• Система автоматически проверяет сообщения\n\n"
        
        "🎮 **Как работает турнир:**\n"
        "1. Админ: `/start` - начинается турнир\n"
        "2. Игроки: Отправляют 🎰 (только новые!)\n"
        "3. Админ: `/stop` - турнир завершается\n"
        "4. Бот: Определяет победителя\n\n"
        
        "🎯 **Вероятность 777:** 1/64 ≈ 1.56%\n"
        "📊 **Ваша статистика:** 1/105 ≈ 0.95% (менее удачливый)\n\n"
        
        "➕ **Добавьте бота в группу и дайте права администратора!**"
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

async def active_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import config
    
    if update.effective_user.id == config.ADMIN_ID:
        config.BOT_ACTIVE = True
        await update.message.reply_text(
            "✅ **Бот включен!** Теперь реагирую на 🎰 и команды."
        )
    else:
        await update.message.reply_text("⛔ Только администратор!")
