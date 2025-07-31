from datetime import datetime, time
from typing import Dict, Optional

class PrayerTimeCalculator:
    def __init__(self):
        self.prayer_times = [
            "Midnight",
            "Fajr",
            "Sunrise",
            "Dhuhr",
            "Asr",
            "Maghrib",
            "Isha"
        ]

    def time_str_to_time(self, time_str: str) -> time:
        """Преобразует строку времени в объект time"""
        return datetime.strptime(time_str, "%H:%M").time()

    def get_next_prayer_time(self, current_time: time, prayer_times: Dict[str, str]) -> Optional[str]:
        """
        Находит следующее время молитвы после текущего времени
        Args:
            current_time: текущее время
            prayer_times: словарь с временами молитв в формате {"Midnight": "00:00", ...}
        Returns:
            Время следующей молитвы в формате "HH:MM"
        """
        # Преобразуем все времена молитв в объекты time
        prayer_times_list = [(prayer, self.time_str_to_time(time_str)) 
                           for prayer, time_str in prayer_times.items()]
        
        # Сортируем времена молитв
        prayer_times_list.sort(key=lambda x: x[1])
        
        # Находим текущую молитву
        current_prayer = None
        for prayer, prayer_time in prayer_times_list:
            if prayer_time > current_time:
                return prayer_times[prayer]
        
        # Если текущее время позже всех молитв сегодня, возвращаем первую молитву следующего дня
        return prayer_times[prayer_times_list[0][0]]

    def get_time_until_next_prayer(self, current_time: time, next_prayer_time: str) -> str:
        """
        Вычисляет время до следующей молитвы
        Args:
            current_time: текущее время
            next_prayer_time: время следующей молитвы в формате "HH:MM"
        Returns:
            Оставшееся время в формате "HH:MM"
        """
        next_time = self.time_str_to_time(next_prayer_time)
        today = datetime.now()
        
        # Если следующая молитва сегодня
        if next_time > current_time:
            time_until = datetime.combine(today, next_time) - datetime.combine(today, current_time)
        else:  # Если следующая молитва завтра
            time_until = datetime.combine(today + timedelta(days=1), next_time) - datetime.combine(today, current_time)
        
        # Преобразуем в формат "HH:MM"
        hours = time_until.seconds // 3600
        minutes = (time_until.seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

# Создаем глобальный экземпляр для использования в других модулях
prayer_time_calculator = PrayerTimeCalculator()
