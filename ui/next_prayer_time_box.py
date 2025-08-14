from kivy.clock import Clock
import os
import subprocess
import logging
import threading
import mpv
import time
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.animation import Animation
from datetime import datetime, timedelta
from kivy.core.text import LabelBase
from kivy.logger import Logger
from logic.prayer_times import prayer_times_manager
from logic.prayer_time_calculator import prayer_time_calculator
from utils.logger import logger  # Импорт логгера

class NextPrayerTimeBox(GridLayout):
    """
    Виджет для отображения времени до следующей молитвы с автообновлением.
    Обновляется каждую минуту для отображения актуального времени до следующей молитвы.
    """
    
    next_prayer_time = StringProperty('00:00')
    time_until = StringProperty('00:00')
    base_font_size = NumericProperty(20)
    
    # Глобальная блокировка для предотвращения одновременного воспроизведения звука
    _sound_lock = threading.Lock()
    _last_sound_time = 0
    _current_player = None  # Текущий экземпляр плеера
    
    @classmethod
    def stop_playback(cls):
        """
        Останавливает текущее воспроизведение звука, если оно активно.
        Возвращает True, если воспроизведение было остановлено, иначе False.
        """
        with cls._sound_lock:
            if cls._current_player is not None:
                try:
                    player = cls._current_player
                    cls._current_player = None  # Сначала обнуляем ссылку, чтобы избежать рекурсии
                    
                    # Устанавливаем громкость на 0 и принудительно останавливаем
                    try:
                        player.volume = 0
                        player.command('stop')
                    except Exception as e:
                        logger.error(f"Ошибка при попытке остановить плеер: {e}")
                    
                    # Даем время на корректную остановку
                    import time
                    time.sleep(0.1)
                    
                    # Завершаем работу плеера
                    try:
                        player.terminate()
                    except Exception as e:
                        Logger.debug(f'Error terminating player: {e}')
                    
                    # Освобождаем ресурсы
                    try:
                        del player
                    except Exception as e:
                        Logger.debug(f'Error releasing player resources: {e}')
                    
                    # Принудительный сбор мусора
                    import gc
                    gc.collect()
                    
                    Logger.debug('Sound playback stopped')
                    return True
                except Exception as e:
                    Logger.error(f'Critical error while stopping playback: {e}')
                    cls._current_player = None
                    return False
            return False
    
    # Ссылка на главное приложение для доступа к часам
    app = ObjectProperty(None)
    
    def __init__(self, base_font_size, app=None, debug_mode=False, **kwargs):
        # Используем SVG иконки
        super().__init__(**kwargs)
        self.app = app
        self.debug_mode = debug_mode  # Режим отладки (по умолчанию выключен)
        self.base_font_size = base_font_size
        self.cols = 3
        self.size_hint_x = 1
        self.size_hint_y = None
        self.height = base_font_size * 0.7  # Увеличили высоту контейнера
        self.padding = [0, base_font_size * 0, 0, base_font_size * 0]  # Добавили отступы сверху и снизу
        
        # Для анимации мигания времени следующего намаза
        self._is_time_blinking = False
        self._blink_event = None
        self._blink_opacity = 1.0
        self._blink_direction = -1  # Направление изменения прозрачности
        
        # Для анимации предупреждения за 30 минут
        self._is_30min_warning = False
        self._30min_blink_event = None
        self._30min_blink_opacity = 1.0
        self._30min_blink_direction = -1
        
        # Для анимации предупреждения за 45 минут
        self._is_45min_warning = False
        self._45min_blink_event = None
        self._45min_blink_opacity = 1.0
        self._45min_blink_direction = -1
        
        # Для анимации предупреждения за 60 минут
        self._is_60min_warning = False
        self._60min_blink_event = None
        self._60min_blink_opacity = 1.0
        self._60min_blink_direction = -1
        
        # Цвета для анимации иконок
        self.normal_icon_color = (0.6, 0.5, 0.0, 1)  # Темно-желтый
        self.highlight_icon_color = (1.0, 0.84, 0.0, 1)  # Ярко-желтый
        self.black_color = (0, 0, 0, 1)  # Черный цвет
        self.is_animating = False
        self.animation_duration = 0.75  # Длительность анимации в секундах
        
        # Создаем иконки молитвенного времени (используем иконку prayer_times из Material Symbols)
        self.prayer_icon_left = Label(
            text='\ueab2',  # Код иконки prayer_times из Material Symbols
            font_name=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf'),
            font_size=base_font_size * 0.5,
            color=self.normal_icon_color  # Используем свойство для цвета
        )
        
        self.time_label = Label(
            text='00:00',
            font_name='FontDSEG7-Bold',
            font_size=base_font_size * 0.55,
            color=(1, 0, 0, 1),  # Красный для времени следующей молитвы
            halign='center',
            size_hint_x=1
        )
        # Отключаем анимацию для свойства opacity, устанавливая его напрямую
        self.time_label.opacity = 1.0
        # Отключаем анимацию через стиль
        from kivy.animation import Animation
        Animation.cancel_all(self.time_label, 'opacity')
        
        self.prayer_icon_right = Label(
            text='\uf353',  # Код иконки prayer_times из Material Symbols
            font_name=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf'),
            font_size=base_font_size * 0.5,
            color=self.normal_icon_color  # Используем свойство для цвета
        )
        
        # Добавляем виджеты в layout
        self.add_widget(self.prayer_icon_left)
        self.add_widget(self.time_label)
        self.add_widget(self.prayer_icon_right)
        
        # Запускаем обновление каждую минуту
        self._update_event = None
        
        # Немедленное обновление времени при создании виджета
        self.update_time()
        
    def on_kv_post(self, *args):
        # Запускаем таймер после инициализации виджета в дереве
        self._update_event = Clock.schedule_interval(lambda dt: self.update_time(), 5)  # Обновляем каждую секунду
        
    def animate_icons(self, *args):
        """Анимация изменения цвета иконок"""
        logger.debug("Запуск анимации иконок")
        
        if self.is_animating:
            logger.debug("Анимация уже запущена, пропускаем")
            return
            
        self.is_animating = True
        logger.debug("Установлен флаг is_animating = True")
        
        # Останавливаем предыдущие анимации, если они есть
        if hasattr(self, '_anim_left'):
            logger.debug("Отмена предыдущей анимации левой иконки")
            self._anim_left.cancel(self.prayer_icon_left)
        if hasattr(self, '_anim_right'):
            logger.debug("Отмена предыдущей анимации правой иконки")
            self._anim_right.cancel(self.prayer_icon_right)
        
        # Запускаем анимацию часов, если доступно приложение
        if self.app and hasattr(self.app, 'start_clock_animation'):
            logger.debug("Запуск анимации часов")
            self.app.start_clock_animation()
        else:
            logger.warning("У приложения нет метода start_clock_animation")
            logger.debug(f"Доступные методы: {[m for m in dir(self.app) if not m.startswith('_')]}")
        
        # Если есть ссылка на PrayerTimesBox, запускаем его анимацию
        if hasattr(self, 'prayer_times_box') and self.prayer_times_box:
            try:
                if hasattr(self.prayer_times_box, 'start_animation'):
                    logger.debug("Запуск анимации списка молитв")
                    self.prayer_times_box.start_animation()
                else:
                    logger.warning("У prayer_times_box нет метода start_animation")
            except Exception as e:
                logger.error(f"Ошибка при запуске анимации списка молитв: {e}")
        else:
            logger.debug("Нет доступа к prayer_times_box для запуска анимации")
        
        # Останавливаем анимацию через 1 минуту
        logger.debug("Планируем остановку анимации через 60 секунд")
        Clock.schedule_once(self.stop_animation, 60)
    
    def stop_animation(self, *args):
        """Останавливаем анимацию иконок"""
        if not self.is_animating:
            return
            
        logger.debug("Остановка анимации иконок")
        self.is_animating = False
        
        # Отменяем предыдущие анимации
        if hasattr(self, '_anim_left'):
            self._anim_left.cancel(self.prayer_icon_left)
            
        # Возвращаем иконки в исходное состояние (темно-желтый цвет, полная непрозрачность)
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
        self.prayer_icon_left.opacity = 1.0
        self.prayer_icon_right.opacity = 1.0
        if hasattr(self, '_anim_right'):
            self._anim_right.cancel(self.prayer_icon_right)
        
        # Возвращаем исходный цвет
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
        
        # Останавливаем анимацию часов, если доступно приложение
        if self.app and hasattr(self.app, 'stop_clock_animation'):
            Logger.debug('Stopping clock animation')
            self.app.stop_clock_animation()
            
        # Останавливаем анимацию списка молитв, если есть ссылка
        if hasattr(self, 'prayer_times_box') and self.prayer_times_box:
            Logger.debug('Stopping prayer list animation')
            self.prayer_times_box.stop_animation()
            
        # Отменяем запланированные события
        if hasattr(self, '_stop_event') and self._stop_event:
            self._stop_event.cancel()
            self._stop_event = None
            
        # Останавливаем мигание времени, если оно активно
        self._stop_time_blink()
    
    def _update_time_blink(self, dt):
        """Обновление мигания времени следующего намаза
        
        Параметры:
        - Прозрачность переключается между 1.0 (видимый) и 0.0 (прозрачный)
        - Частота переключения: 500 мс (0.5 секунды)
        - Без анимации - только мгновенное переключение
        """
        if not self._is_time_blinking or not hasattr(self, 'time_label'):
            return
            
        # Мгновенное переключение видимости
        self.time_label.opacity = 0.0 if self.time_label.opacity == 1.0 else 1.0
    
    def _play_sound_file(self, sound_file, is_adhan=False):
        """
        Воспроизводит звуковой файл в отдельном потоке
        
        Args:
            sound_file (str): Путь к звуковому файлу для воспроизведения
            is_adhan (bool): Флаг, указывающий, что воспроизводится азан
            
        Returns:
            bool: True, если воспроизведение успешно запущено, иначе False
        """
        if not os.path.exists(sound_file):
            Logger.error(f'File not found: {sound_file}')
            return False
            
        Logger.debug(f'Starting playback of file: {sound_file}')
        player = None
        
        try:
            # Создаем экземпляр MPV-плеера с минимальными настройками
            with NextPrayerTimeBox._sound_lock:
                # Останавливаем текущее воспроизведение, если оно есть
                if NextPrayerTimeBox._current_player is not None:
                    NextPrayerTimeBox.stop_playback()
                
                # Создаем новый экземпляр плеера
                try:
                    player = mpv.MPV(
                        vo='null',      # Без видеовыхода
                        quiet=True,     # Тихий режим
                        loglevel='fatal', # Только критические ошибки
                        input_default_bindings=True,
                        input_vo_keyboard=True,
                        input_cursor=False,
                        cursor_autohide='no',
                        msg_level='all=error'
                    )
                    
                    # Устанавливаем обработчики событий
                    @player.event_callback('end-file')
                    def on_end(event):
                        # Этот колбэк будет вызван при завершении воспроизведения
                        Logger.debug(f'Playback completed: {sound_file}')
                        
                    # Сохраняем ссылку на текущий плеер
                    NextPrayerTimeBox._current_player = player
                    
                except Exception as e:
                    Logger.error(f'Error creating MPV player: {e}')
                    if player:
                        try:
                            player.terminate()
                        except:
                            pass
                    return False
            
            # Воспроизводим звук
            Logger.debug(f'Starting playback: {sound_file}')
            player.play(sound_file)
            
            # Ждем завершения воспроизведения с таймаутом
            try:
                # Ждем окончания воспроизведения с таймаутом
                # (таймаут в секундах, None означает бесконечно)
                player.wait_for_playback(timeout=None)
            except Exception as e:
                Logger.debug(f'Error while waiting for playback to complete: {e}')
            
            # Даем время на корректное завершение
            import time
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            error_msg = f"Critical error while playing sound {sound_file}: {str(e)}"
            Logger.error(error_msg)
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Всегда освобождаем ресурсы
            with NextPrayerTimeBox._sound_lock:
                if NextPrayerTimeBox._current_player is player:
                    NextPrayerTimeBox._current_player = None
                
                if player:
                    try:
                        # Плавно уменьшаем громкость перед остановкой
                        try:
                            player.volume = 0
                            player.command('stop')
                            time.sleep(0.1)
                        except:
                            pass
                            
                        # Завершаем работу плеера
                        try:
                            player.terminate()
                        except:
                            pass
                            
                        # Явно освобождаем ресурсы
                        try:
                            del player
                        except:
                            pass
                            
                        # Принудительный сбор мусора
                        import gc
                        gc.collect()
                        
                    except Exception as e:
                        Logger.debug(f'Error releasing player resources: {e}')
    
    def _play_notification_sound(self, notification_type='15min'):
        """
        Воспроизведение звукового уведомления в отдельном потоке
        
        Args:
            notification_type (str): Тип уведомления ('15min', '30min', '45min', '60min' или 'prayer_change')
        """
        with NextPrayerTimeBox._sound_lock:
            current_time = time.time()
            # Проверяем, что с момента последнего воспроизведения прошло больше 30 секунд
            if current_time - NextPrayerTimeBox._last_sound_time < 30:
                Logger.debug('Skipping sound playback: 30 seconds have not passed since last playback')
                return
            
            NextPrayerTimeBox._last_sound_time = current_time
            
        Logger.debug(f'Starting notification playback: {notification_type}')
        
        # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
        def play_sounds():
            try:
                # Получаем путь к корневой папке проекта
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Выбираем файл в зависимости от типа уведомления
                if notification_type == 'prayer_change':
                    sound_file = os.path.join(project_dir, 'audio', 'notice', 'Ahmet', 'Ahmet-VaxtGirdi.mp3')
                    adhan_file = os.path.join(project_dir, 'audio', 'adhan', 'Adhan01.mp3')
                    
                    # Воспроизводим первый звук
                    if os.path.exists(sound_file):
                        self._play_sound_file(sound_file)
                    else:
                        Logger.error(f'Notification file not found: {sound_file}')
                    
                    # Воспроизводим азан
                    if os.path.exists(adhan_file):
                        Logger.debug('Playing adhan after prayer change')
                        self._play_sound_file(adhan_file, is_adhan=True)
                    else:
                        Logger.error(f'Adhan file not found: {adhan_file}')
                    
                else:  # Для других типов уведомлений
                    if notification_type == '30min':
                        sound_file = os.path.join(project_dir, 'audio', 'notice', 'Ahmet', 'Ahmet-30dakikakaldi.mp3')
                    elif notification_type == '45min':
                        sound_file = os.path.join(project_dir, 'audio', 'notice', 'Ahmet', 'Ahmet-45dakikakaldi.mp3')
                    elif notification_type == '60min':
                        sound_file = os.path.join(project_dir, 'audio', 'notice', 'Ahmet', 'Ahmet-60dakikakaldi.mp3')
                    else:  # По умолчанию 15-минутное уведомление
                        sound_file = os.path.join(project_dir, 'audio', 'notice', 'Ahmet', 'Ahmet-15dakikakaldi.mp3')
                    
                    Logger.debug(f'Checking file: {sound_file}')
                    
                    if os.path.exists(sound_file):
                        self._play_sound_file(sound_file)
                    else:
                        error_msg = f"Notification file not found: {sound_file}"
                        Logger.error(error_msg)
                        logging.error(error_msg)
                
                # Заменяем '30min' на '30 min' и т.д. для лучшей читаемости
                pretty_notification = notification_type.replace('min', ' min') if 'min' in notification_type else notification_type
                logging.info(f"Notification: Playing notification: {pretty_notification}")
                
            except Exception as e:
                error_msg = f"Error playing notification {notification_type}: {str(e)}"
                Logger.error(error_msg)
                logging.error(error_msg, exc_info=True)
        
        # Запускаем поток с воспроизведением звуков
        import threading
        sound_thread = threading.Thread(target=play_sounds, daemon=True)
        sound_thread.start()
        
        return True
    
    def _start_time_blink(self):
        """Запуск анимации мигания времени следующего намаза"""
        if self._is_time_blinking:
            Logger.debug('Animation already running, skipping restart')
            return
            
        Logger.debug('Starting next prayer time blinking animation')
        self._is_time_blinking = True
        self._blink_opacity = 1.0
        
        # Воспроизводим звуковое уведомление для 15-минутного предупреждения
        Logger.debug('Starting 15-minute sound notification')
        self._play_notification_sound(notification_type='15min')
        
        # Запускаем обновление анимации каждые 500 мс
        self._blink_event = Clock.schedule_interval(self._update_time_blink, 0.5)
        
    def _stop_time_blink(self):
        """Остановка анимации мигания времени следующего намаза"""
        if not self._is_time_blinking:
            return
            
        Logger.debug('Stopping next prayer time blinking')
        self._is_time_blinking = False
        
        # Отменяем запланированное обновление
        if self._blink_event:
            self._blink_event.cancel()
            self._blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
            
    def _update_30min_blink(self, dt):
        """Обновление анимации мигания предупреждения за 30 минут"""
        if not self._is_30min_warning or not hasattr(self, 'time_label'):
            return
            
        # Мгновенное переключение видимости
        self.time_label.opacity = 0.0 if self.time_label.opacity == 1.0 else 1.0
    
    def _start_60min_warning(self):
        """Запуск анимации предупреждения за 60 минут"""
        if self._is_60min_warning:
            Logger.debug('60-minute animation already running, skipping restart')
            return
            
        Logger.debug('Starting 60-minute warning animation')
        self._is_60min_warning = True
        self._60min_blink_opacity = 1.0
        self._60min_blink_direction = -1
        
        # Воспроизводим звуковое уведомление для 60-минутного предупреждения
        Logger.debug('Starting 60-minute sound notification')
        self._play_notification_sound(notification_type='60min')
        
        # Запускаем обновление анимации каждые 100 мс
        self._60min_blink_event = Clock.schedule_interval(self._update_60min_blink, 0.1)
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(lambda dt: self._stop_60min_warning(), 60)
        
    def _update_60min_blink(self, dt):
        """Обновление анимации мигания предупреждения за 60 минут"""
        if not self._is_60min_warning or not hasattr(self, 'time_label'):
            return
            
        # Мгновенное переключение видимости
        self.time_label.opacity = 0.0 if self.time_label.opacity == 1.0 else 1.0
        
    def _stop_60min_warning(self):
        """Остановка анимации предупреждения за 60 минут"""
        if not self._is_60min_warning:
            return
            
        Logger.debug('Stopping 60-minute warning animation')
        self._is_60min_warning = False
        
        # Отменяем запланированное обновление
        if self._60min_blink_event:
            self._60min_blink_event.cancel()
            self._60min_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
            
    def _start_45min_warning(self):
        """Запуск анимации предупреждения за 45 минут"""
        if self._is_45min_warning:
            Logger.debug('45-minute animation already running, skipping restart')
            return
            
        Logger.debug('Starting 45-minute warning animation')
        self._is_45min_warning = True
        self._45min_blink_opacity = 1.0
        self._45min_blink_direction = -1
        
        # Воспроизводим звуковое уведомление для 45-минутного предупреждения
        Logger.debug('Starting 45-minute sound notification')
        self._play_notification_sound(notification_type='45min')
        
        # Запускаем обновление анимации каждые 100 мс
        self._45min_blink_event = Clock.schedule_interval(self._update_45min_blink, 0.1)
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(lambda dt: self._stop_45min_warning(), 60)
        
    def _update_45min_blink(self, dt):
        """Обновление анимации мигания предупреждения за 45 минут"""
        if not self._is_45min_warning or not hasattr(self, 'time_label'):
            return
            
        # Мгновенное переключение видимости
        self.time_label.opacity = 0.0 if self.time_label.opacity == 1.0 else 1.0
        
    def _stop_45min_warning(self):
        """Остановка анимации предупреждения за 45 минут"""
        if not self._is_45min_warning:
            return
            
        Logger.debug('Stopping 45-minute warning animation')
        self._is_45min_warning = False
        
        # Отменяем запланированное обновление
        if self._45min_blink_event:
            self._45min_blink_event.cancel()
            self._45min_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
            
    def _start_30min_warning(self):
        """Запуск анимации предупреждения за 30 минут"""
        if self._is_30min_warning:
            return
            
        Logger.debug('Starting 30-minute warning animation')
        self._is_30min_warning = True
        self._30min_blink_opacity = 1.0
        self._30min_blink_direction = -1  # Начинаем с уменьшения прозрачности
        
        # Запускаем обновление анимации каждые 100 мс
        self._30min_blink_event = Clock.schedule_interval(self._update_30min_blink, 0.1)
        
        # Воспроизводим звуковое уведомление
        Logger.debug('Starting 30-minute sound notification')
        self._play_notification_sound(notification_type='30min')
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(lambda dt: self._stop_30min_warning(), 60)
    
    def _stop_30min_warning(self):
        """Остановка анимации предупреждения за 30 минут"""
        if not self._is_30min_warning:
            return
            
        Logger.debug('Stopping 30-minute warning animation')
        self._is_30min_warning = False
        
        # Отменяем запланированное обновление
        if self._30min_blink_event:
            self._30min_blink_event.cancel()
            self._30min_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
    
    def _is_within_15_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза 15 минут или меньше"""
        return self._get_minutes_until_prayer(current_time, next_prayer_time_str) <= 15
    
    def _is_exactly_30_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза ровно 30 минут"""
        minutes = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
        return minutes == 30
        
    def _is_exactly_45_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза ровно 45 минут"""
        minutes = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
        return minutes == 45
        
    def _is_exactly_60_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза ровно 60 минут, включая случай с переходом на следующий день"""
        try:
            # Преобразуем время намаза в объект datetime
            prayer_time = datetime.strptime(next_prayer_time_str, '%H:%M').time()
            
            # Получаем текущую дату
            current_date = datetime.now().date()
            
            # Создаем объекты datetime для текущего времени и времени намаза
            current_dt = datetime.combine(current_date, current_time)
            prayer_dt = datetime.combine(current_date, prayer_time)
            
            # Если время намаза уже прошло сегодня, берем намаз на следующий день
            if prayer_dt <= current_dt:
                prayer_dt += timedelta(days=1)
                Logger.debug(f'Prayer time {next_prayer_time_str} moved to the next day')
            
            # Вычисляем разницу во времени
            time_diff = prayer_dt - current_dt
            
            # Преобразуем разницу в минуты
            minutes = int(time_diff.total_seconds() / 60)
            
            Logger.debug(f'60-minute check: current_time={current_time}, prayer_time={prayer_dt.time()}, minutes_left={minutes}')
            
            if minutes == 60:
                Logger.debug(f'Found 60 minutes before prayer {prayer_dt.time()}')
                return True
            else:
                Logger.debug(f'Time until prayer {prayer_dt.time()}: {minutes} minutes (not 60)')
                return False
                
        except Exception as e:
            Logger.error(f'Error checking 60 minutes before prayer: {e}')
            import traceback
            traceback.print_exc()
            return False
    
    def _get_minutes_until_prayer(self, current_time, next_prayer_time_str):
        """Возвращает количество минут до намаза"""
        try:
            # Преобразуем время намаза в объект datetime
            prayer_time = datetime.strptime(next_prayer_time_str, '%H:%M').time()
            
            # Получаем текущую дату
            current_date = datetime.now().date()
            
            # Создаем объекты datetime для текущего времени и времени намаза
            current_dt = datetime.combine(current_date, current_time)
            prayer_dt = datetime.combine(current_date, prayer_time)
            
            # Если время намаза уже прошло сегодня, берем намаз на следующий день
            if prayer_dt < current_dt:
                prayer_dt += timedelta(days=1)
                Logger.debug(f'Prayer time {next_prayer_time_str} moved to the next day')
            
            # Вычисляем разницу во времени
            time_diff = prayer_dt - current_dt
            
            # Преобразуем разницу в минуты
            minutes = int(time_diff.total_seconds() / 60)
            
            Logger.debug(f'Calculating time until prayer: current={current_time}, prayer={next_prayer_time_str}, minutes_until={minutes}')
            
            return minutes
                
        except Exception as e:
            Logger.error(f'Error calculating time until prayer: {e}')
            import traceback
            traceback.print_exc()
            return 0
    
    def _check_prayer_time(self, current_time, next_prayer_time_str):
        """
        Проверяет оставшееся время до намаза и возвращает кортеж (найдено_совпадение, минут_до_намаза)
        
        Args:
            current_time: Текущее время
            next_prayer_time_str: Время следующего намаза в формате 'ЧЧ:ММ'
            
        Returns:
            tuple: (bool, int) - (найдено_совпадение, минут_до_намаза)
        """
        minutes = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
        
        # Добавляем проверку на уже показанное уведомление
        if hasattr(self, '_last_notification_minutes') and self._last_notification_minutes == minutes:
            return False, minutes
            
        Logger.debug(f'Checking time until prayer: {minutes} minutes')
        
        # Проверяем все временные интервалы
        if minutes in [15, 30, 45, 60]:
            Logger.debug(f'Found {minutes} minutes until prayer')
            self._last_notification_minutes = minutes
            return True, minutes
            
        return False, minutes
    
    def _start_yellow_text_blink(self):
        """Запуск анимации мигания желтого текста следующего намаза"""
        if hasattr(self, '_is_yellow_text_blinking') and self._is_yellow_text_blinking:
            Logger.debug('Yellow text blink animation already running')
            return
            
        Logger.debug('Starting next prayer yellow text blinking')
        self._is_yellow_text_blinking = True
        self._yellow_text_blink_opacity = 1.0
        
        # Запускаем обновление анимации каждые 500 мс
        self._yellow_text_blink_event = Clock.schedule_interval(self._update_yellow_text_blink, 0.5)
    
    def _update_yellow_text_blink(self, dt):
        """Обновление анимации мигания желтого текста
        
        Параметры анимации:
        - Прозрачность переключается между 1.0 (полностью видимый) и 0.0 (полностью прозрачный)
        - Частота обновления: 500 мс (0.5 секунды)
        - Без плавности - мгновенное переключение
        """
        if not hasattr(self, '_is_yellow_text_blinking') or not self._is_yellow_text_blinking:
            return
            
        # Мгновенное переключение между 0.0 и 1.0 без плавности
        self._yellow_text_blink_opacity = 0.0 if self._yellow_text_blink_opacity == 1.0 else 1.0
            
        # Применяем прозрачность к метке времени и названию следующего намаза
        if hasattr(self, 'prayer_times_box'):
            next_prayer = self._get_next_prayer_key()
            if next_prayer and next_prayer in self.prayer_times_box.prayer_labels:
                labels = self.prayer_times_box.prayer_labels[next_prayer]
                # Устанавливаем прозрачность без анимации
                # Устанавливаем полную видимость без анимации
                labels['time_label'].opacity = 1.0
                labels['name_label'].opacity = 1.0
                labels['time_label'].opacity = self._yellow_text_blink_opacity
                labels['name_label'].opacity = self._yellow_text_blink_opacity
    
    def _stop_yellow_text_blink(self):
        """Остановка анимации мигания желтого текста"""
        if not hasattr(self, '_is_yellow_text_blinking') or not self._is_yellow_text_blinking:
            return
            
        Logger.debug('Stopping next prayer yellow text blinking')
        self._is_yellow_text_blinking = False
        
        # Отменяем запланированное обновление
        if hasattr(self, '_yellow_text_blink_event') and self._yellow_text_blink_event:
            self._yellow_text_blink_event.cancel()
            self._yellow_text_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'prayer_times_box'):
            next_prayer = self._get_next_prayer_key()
            if next_prayer and next_prayer in self.prayer_times_box.prayer_labels:
                labels = self.prayer_times_box.prayer_labels[next_prayer]
                labels['time_label'].opacity = 1.0
                labels['name_label'].opacity = 1.0
    
    def _get_next_prayer_key(self):
        """Возвращает ключ следующей молитвы"""
        if not hasattr(self, 'prayer_times_box') or not hasattr(self.prayer_times_box, 'prayer_mapping'):
            return None
            
        current_time = datetime.now().time()
        prayer_times_data = prayer_times_manager.get_prayer_times()
        
        # Находим следующую молитву
        next_prayer_time_str = prayer_time_calculator.get_next_prayer_time(
            current_time, 
            prayer_times_data
        )
        
        # Находим ключ следующей молитвы
        for key, value in self.prayer_times_box.prayer_mapping.items():
            if value in prayer_times_data and prayer_times_data[value] == next_prayer_time_str:
                return value
                
        return None
    
    def _stop_all_animations(self):
        """
        Останавливает все активные анимации уведомлений.
        Используется перед запуском новой анимации, чтобы избежать конфликтов.
        """
        # Останавливаем анимацию мигания времени
        self._stop_time_blink()
        
        # Останавливаем анимацию мигания желтого текста
        self._stop_yellow_text_blink()
        
        # Останавливаем анимации предупреждений
        if hasattr(self, '_stop_30min_warning'):
            self._stop_30min_warning()
        if hasattr(self, '_stop_45min_warning'):
            self._stop_45min_warning()
        if hasattr(self, '_stop_60min_warning'):
            self._stop_60min_warning()
            
        if self._is_45min_warning:
            Logger.debug('Stopping 45-minute warning')
            self._stop_45min_warning()
            
            Logger.debug('Stopping 60-minute warning')
            self._stop_60min_warning()
    
    def _handle_prayer_notification(self, minutes_left, next_prayer_time_str):
        """
        Обрабатывает уведомление о времени до намаза.
        
        Args:
            minutes_left (int): Количество минут до намаза (15, 30, 45, 60)
            next_prayer_time_str (str): Время следующего намаза в формате 'ЧЧ:ММ'
        """
        Logger.debug(f'Processing notification {minutes_left} minutes before prayer {next_prayer_time_str}')
        
        # Останавливаем все текущие анимации
        self._stop_all_animations()
        
        # Запускаем соответствующую анимацию и звуковое уведомление
        if minutes_left == 15:
            Logger.debug('Starting time blink animation (15 minutes)')
            self._start_time_blink()  # Мигание красных цифр
            self._start_yellow_text_blink()  # Мигание желтого текста
            self._play_notification_sound('15min')
            # Устанавливаем таймер на остановку анимации желтого текста через 1 минуту
            Clock.schedule_once(lambda dt: self._stop_yellow_text_blink() if hasattr(self, '_stop_yellow_text_blink') else None, 60)
        elif minutes_left == 30:
            Logger.debug('Starting 30-minute warning')
            self._start_30min_warning()
            self._start_yellow_text_blink()  # Мигание желтого текста
            self._play_notification_sound('30min')
            # Устанавливаем таймер на остановку анимаций через 1 минуту
            Clock.schedule_once(lambda dt: self._stop_30min_warning() if hasattr(self, '_stop_30min_warning') else None, 60)
            Clock.schedule_once(lambda dt: self._stop_yellow_text_blink() if hasattr(self, '_stop_yellow_text_blink') else None, 60)
        elif minutes_left == 45:
            Logger.debug('Starting 45-minute warning')
            self._start_45min_warning()
            self._start_yellow_text_blink()  # Мигание желтого текста
            self._play_notification_sound('45min')
            # Устанавливаем таймер на остановку анимаций через 1 минуту
            Clock.schedule_once(lambda dt: self._stop_45min_warning() if hasattr(self, '_stop_45min_warning') else None, 60)
            Clock.schedule_once(lambda dt: self._stop_yellow_text_blink() if hasattr(self, '_stop_yellow_text_blink') else None, 60)
        elif minutes_left == 60:
            Logger.debug('Starting 60-minute warning')
            self._start_60min_warning()
            self._start_yellow_text_blink()  # Мигание желтого текста
            self._play_notification_sound('60min')
            # Устанавливаем таймер на остановку анимаций через 1 минуту
            Clock.schedule_once(lambda dt: self._stop_60min_warning() if hasattr(self, '_stop_60min_warning') else None, 60)
            Clock.schedule_once(lambda dt: self._stop_yellow_text_blink() if hasattr(self, '_stop_yellow_text_blink') else None, 60)
    
    def update_time(self):
        """Обновляет отображаемое время до следующей молитвы"""
        try:
            # Получаем текущее время
            now = datetime.now()
            current_time = now.time()
            
            # Получаем времена молитв (кешируем вызов)
            if not hasattr(self, '_last_prayer_times_update') or (now - self._last_prayer_times_update).total_seconds() > 60:
                self._prayer_times_cache = prayer_times_manager.get_prayer_times()
                self._last_prayer_times_update = now
            
            # Находим следующую молитву
            next_prayer_time_str = prayer_time_calculator.get_next_prayer_time(
                current_time, 
                self._prayer_times_cache)
            
            # Проверяем, нужно ли показать уведомление
            is_notification_time, minutes_left = self._check_prayer_time(current_time, next_prayer_time_str)
            
            # Если пришло время для уведомления, обрабатываем его
            if is_notification_time:
                self._handle_prayer_notification(minutes_left, next_prayer_time_str)
            else:
                # Если уведомление не требуется, проверяем, не нужно ли остановить анимации
                # Это нужно, если пользователь изменил время вручную или произошел сдвиг времени
                current_minutes = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
                
                # Останавливаем анимации, если они активны, но условия для них больше не выполняются
                if self._is_time_blinking and current_minutes != 15:
                    Logger.debug('Stopping time blink animation (conditions not met)')
                    self._stop_time_blink()
                    
                if hasattr(self, '_is_yellow_text_blinking') and self._is_yellow_text_blinking and current_minutes not in [15, 30, 45, 60]:
                    Logger.debug('Stopping yellow text blink (conditions not met)')
                    self._stop_yellow_text_blink()
                    
                if self._is_30min_warning and current_minutes != 30:
                    Logger.debug('Stopping 30-minute warning (conditions not met)')
                    self._stop_30min_warning()
                    
                if self._is_45min_warning and current_minutes != 45:
                    Logger.debug('Stopping 45-minute warning (conditions not met)')
                    self._stop_45min_warning()
                    
                if self._is_60min_warning and current_minutes != 60:
                    Logger.debug('Stopping 60-minute warning (conditions not met)')
                    self._stop_60min_warning()
            
            # Продолжаем с оставшейся частью метода
            prayer_time = datetime.strptime(next_prayer_time_str, '%H:%M').time()
            current_date = now.date()
            prayer_datetime = datetime.combine(current_date, prayer_time)
            
            # Если время намаза уже прошло сегодня, берем намаз на следующий день
            if prayer_datetime < now:
                prayer_datetime += timedelta(days=1)
                
            # Вычисляем разницу во времени
            time_diff = prayer_datetime - now
            
            # Преобразуем разницу в часы и минуты
            total_seconds = int(time_diff.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Форматируем строку с оставшимся временем в формате ЧЧ:ММ
            time_until_str = f"{hours:02d}:{minutes:02d}"
            
            # Обновляем свойство, чтобы обновить отображение
            self.time_until = time_until_str
            
            # Обновляем время следующего намаза
            self.next_prayer_time = next_prayer_time_str
            
            # Обновляем текст в time_label (оставшееся время до намаза)
            self.time_label.text = time_until_str
            
            # Проверяем, изменилось ли время следующего намаза (а не оставшееся время)
            current_next_prayer = f"{next_prayer_time_str}"
            if hasattr(self, 'previous_next_prayer'):
                if self.previous_next_prayer != current_next_prayer:
                    if self.debug_mode:
                        logger.debug(f"Prayer time changed from {self.previous_next_prayer} to {current_next_prayer}")
                    # Если изменилось время намаза, запускаем анимацию и воспроизводим азан
                    self.animate_icons()
                    self._play_notification_sound('prayer_change')
            
            # Сохраняем текущее время следующего намаза для следующей проверки
            self.previous_next_prayer = current_next_prayer
            
            if self.debug_mode:
                # Логируем отладочную информацию
                logger.debug(f"Next prayer time: {current_time.strftime('%H:%M:%S')}, "
                           f"Next prayer time: {next_prayer_time_str}, "
                           f"Time until prayer: {time_until_str}" + 
                           (" [BLINKING]" if self._is_time_blinking else ""))
            
        except Exception as e:
            logger.error(f"Error updating prayer time: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Запланировать следующее обновление через 1 секунду
            if hasattr(self, '_update_event') and self._update_event is not None:
                self._update_event.cancel()
                
            self._update_event = Clock.schedule_once(lambda dt: self.update_time(), 1.0)
            
            # Для отладки выводим в консоль информацию о смене времени
            debug_info = f"Current time: {current_time.strftime('%H:%M:%S')}, "
            debug_info += f"Next prayer time: {next_prayer_time_str}, "
            debug_info += f"Time until prayer: {time_until_str}"
            if self._is_time_blinking:
                debug_info += " [BLINKING]"
            Logger.debug(debug_info)
            
    def on_parent(self, widget, parent):
        # Отписываемся от таймера при удалении виджета
        if parent is None and hasattr(self, '_update_event') and self._update_event:
            self._update_event.cancel()
