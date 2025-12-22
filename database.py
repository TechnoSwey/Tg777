import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any
import threading

class TournamentManager:
    """Управление турнирами и статистикой"""
    
    def __init__(self):
        self.active_tournaments: Dict[int, Dict] = {}
        self.player_stats: Dict[int, Dict[int, int]] = {}
        self.lock = threading.Lock()  # Для потокобезопасности
        
        # История турниров (можно сохранять в файл)
        self.tournament_history: List[Dict] = []
    
    def start_tournament(self, chat_id: int, chat_title: str, duration_minutes: Optional[int] = None) -> bool:
        """Запускает турнир в чате"""
        with self.lock:
            if chat_id in self.active_tournaments and self.active_tournaments[chat_id]['is_active']:
                return False  # Турнир уже активен
            
            self.active_tournaments[chat_id] = {
                'start_time': datetime.now(),
                'end_time': datetime.now() + timedelta(minutes=duration_minutes) if duration_minutes else None,
                'chat_title': chat_title,
                'duration_minutes': duration_minutes,
                'is_active': True,
                'message_count': 0
            }
            
            # Инициализируем статистику
            self.player_stats[chat_id] = defaultdict(int)
            
            return True
    
    def stop_tournament(self, chat_id: int) -> Optional[Dict]:
        """Останавливает турнир и возвращает результаты"""
        with self.lock:
            if chat_id not in self.active_tournaments:
                return None
            
            tournament = self.active_tournaments[chat_id].copy()
            tournament['is_active'] = False
            tournament['end_time'] = datetime.now()
            
            # Получаем статистику
            if chat_id in self.player_stats:
                stats = self.player_stats[chat_id]
                sorted_players = sorted(stats.items(), key=lambda x: x[1], reverse=True)
                
                results = {
                    'tournament_data': tournament,
                    'player_stats': dict(sorted_players),
                    'total_wins': sum(stats.values()),
                    'total_players': len(stats)
                }
                
                # Сохраняем в историю
                self.tournament_history.append(results)
                
                # Очищаем активные данные
                del self.active_tournaments[chat_id]
                del self.player_stats[chat_id]
                
                return results
            
            return None
    
    def add_win(self, chat_id: int, user_id: int, user_name: str = "") -> bool:
        """Добавляет победу игроку"""
        with self.lock:
            if chat_id in self.active_tournaments and self.active_tournaments[chat_id]['is_active']:
                self.player_stats[chat_id][user_id] += 1
                
                if chat_id in self.active_tournaments:
                    self.active_tournaments[chat_id]['message_count'] += 1
                
                return True
            return False
    
    def is_tournament_active(self, chat_id: int) -> bool:
        """Проверяет активен ли турнир"""
        return chat_id in self.active_tournaments and self.active_tournaments[chat_id]['is_active']
    
    def get_tournament_info(self, chat_id: int) -> Optional[Dict]:
        """Возвращает информацию о турнире"""
        return self.active_tournaments.get(chat_id)
    
    def get_stats(self, chat_id: int) -> List[Tuple[int, int]]:
        """Возвращает статистику турнира"""
        if chat_id in self.player_stats:
            stats = self.player_stats[chat_id]
            return sorted(stats.items(), key=lambda x: x[1], reverse=True)
        return []
    
    def get_all_active_tournaments(self) -> List[Dict]:
        """Возвращает все активные турниры"""
        return [tournament for tournament in self.active_tournaments.values() if tournament['is_active']]
    
    def save_to_file(self, filename: str = "tournaments_backup.json"):
        """Сохраняет данные в файл (для резервного копирования)"""
        with self.lock:
            data = {
                'active_tournaments': self.active_tournaments,
                'tournament_history': self.tournament_history,
                'backup_time': datetime.now().isoformat()
            }
            
            # Конвертируем datetime в строки для JSON
            def datetime_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, default=datetime_serializer, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename: str = "tournaments_backup.json") -> bool:
        """Загружает данные из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Здесь нужно конвертировать строки обратно в datetime
            # Упрощенная версия - только для истории
            
            if 'tournament_history' in data:
                self.tournament_history = data['tournament_history']
            
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

# Глобальный менеджер турниров
tournament_manager = TournamentManager()
