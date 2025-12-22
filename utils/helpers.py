from datetime import datetime, timedelta
from typing import Optional
import math

def format_duration(seconds: int) -> str:
    """Форматирует длительность в читаемый вид"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}ч {minutes}м {secs}с"
    elif minutes > 0:
        return f"{minutes}м {secs}с"
    else:
        return f"{secs}с"

def format_time_ago(date: datetime) -> str:
    """Возвращает строку вида '5 минут назад'"""
    now = datetime.now(date.tzinfo)
    delta = now - date
    
    if delta.days > 0:
        return f"{delta.days} дней назад"
    
    seconds = delta.seconds
    if seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} час{'ов' if hours % 10 not in [1] else ''} назад"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} минут{'у' if minutes % 10 == 1 and minutes % 100 != 11 else '' if minutes % 10 in [2,3,4] and minutes % 100 not in [12,13,14] else 'ов'} назад"
    else:
        return f"{seconds} секунд{'у' if seconds == 1 else '' if 2 <= seconds % 10 <= 4 and seconds % 100 not in [12,13,14] else 'ов'} назад"

def create_message_link(chat_id: int, message_id: int, chat_username: Optional[str] = None) -> str:
    """Создает ссылку на сообщение в Telegram"""
    if chat_username:
        return f"https://t.me/{chat_username}/{message_id}"
    else:
        # Для приватных чатов без username
        chat_id_str = str(chat_id).replace('-100', '')
        return f"https://t.me/c/{chat_id_str}/{message_id}"

def calculate_probability(successes: int, attempts: int) -> tuple[float, str]:
    """Рассчитывает вероятность и возвращает её в процентах"""
    if attempts == 0:
        return 0.0, "0%"
    
    probability = (successes / attempts) * 100
    return probability, f"{probability:.2f}%"

def get_emoji_for_place(place: int) -> str:
    """Возвращает эмодзи для места в рейтинге"""
    if place == 1:
        return "🥇"
    elif place == 2:
        return "🥈"
    elif place == 3:
        return "🥉"
    elif 4 <= place <= 10:
        return "🏅"
    else:
        return "🎖️"

def format_user_mention(user_id: int, username: Optional[str], first_name: str) -> str:
    """Форматирует упоминание пользователя"""
    if username:
        return f"@{username}"
    else:
        return f"<a href='tg://user?id={user_id}'>{first_name}</a>"
