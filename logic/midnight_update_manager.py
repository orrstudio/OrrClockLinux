from kivy.clock import Clock
from datetime import datetime, timedelta

class MidnightUpdateManager:
    """
    Менеджер автоматического обновления данных и UI ровно в полночь.
    Позволяет регистрировать callback-функции, которые будут вызваны при наступлении нового дня.
    """
    def __init__(self):
        self._callbacks = []
        self._event = None
        self.schedule_next_midnight()

    def register_callback(self, callback):
        """
        Регистрирует функцию, которая будет вызвана в полночь.
        Аргументы:
            callback (callable): функция без аргументов
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback):
        """
        Удаляет ранее зарегистрированный callback.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def schedule_next_midnight(self):
        """
        Планирует обновление на ближайшую полночь.
        """
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = (next_midnight - now).total_seconds()
        if self._event:
            self._event.cancel()
        self._event = Clock.schedule_once(self._on_midnight, seconds_until_midnight)

    def _on_midnight(self, dt):
        """
        Вызывается в полночь, вызывает все callbacks и планирует следующее обновление.
        """
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Ошибка в midnight callback: {e}")
        self.schedule_next_midnight()
