from datetime import datetime
from typing import Optional

class MessageFilter:
    """Фильтры для проверки сообщений"""
    
    def __init__(self, max_age_seconds: int = 120):
        self.max_age_seconds = max_age_seconds
    
    def is_message_fresh(self, message_date: datetime) -> tuple[bool, Optional[str]]:
        """Проверяет, свежее ли сообщение"""
        current_time = datetime.now(message_date.tzinfo)
        age_seconds = (current_time - message_date).total_seconds()
        
        if age_seconds > self.max_age_seconds:
            return False, f"Сообщение слишком старое ({int(age_seconds/60)} минут)"
        
        return True, None
    
    def is_original_message(self, message) -> tuple[bool, Optional[str]]:
        """Проверяет, является ли сообщение оригинальным (не пересланным)"""
        
        check_attributes = [
            ('forward_from', 'Переслано от пользователя'),
            ('forward_from_chat', 'Переслано из чата'),
            ('forward_from_message_id', 'Имеет ID оригинала'),
            ('forward_sender_name', 'Имя отправителя скрыто'),
            ('forward_date', 'Имеет дату оригинала'),
        ]
        
        for attr, reason in check_attributes:
            if hasattr(message, attr) and getattr(message, attr):
                return False, reason
        
        # Проверяем время
        if hasattr(message, 'date'):
            is_fresh, reason = self.is_message_fresh(message.date)
            if not is_fresh:
                return False, reason
        
        return True, None
    
    def is_valid_dice_message(self, message) -> tuple[bool, Optional[str]]:
        """Проверяет, является ли сообщение с эмодзи валидным"""
        
        # Проверяем, что это эмодзи
        if not hasattr(message, 'dice') or not message.dice:
            return False, "Не является эмодзи"
        
        # Проверяем оригинальность
        is_original, reason = self.is_original_message(message)
        if not is_original:
            return False, reason
        
        return True, None

# Создаем глобальный фильтр
message_filter = MessageFilter()
