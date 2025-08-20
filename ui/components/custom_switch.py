from kivy.properties import BooleanProperty, ColorProperty, NumericProperty, ListProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.clock import Clock

class CustomSwitch(AnchorLayout):
    # Основные свойства
    active = BooleanProperty(False)
    """Состояние переключателя (включен/выключен)."""
    
    # Свойства внешнего вида
    thumb_color = ColorProperty([1, 1, 1, 1])
    """Текущий цвет ползунка переключателя (устаревшее, оставлено для обратной совместимости)."""
    
    thumb_color_active = ColorProperty([0, 1, 0, 1])
    """Цвет ползунка во включенном состоянии (зеленый)."""
    
    thumb_color_inactive = ColorProperty([1, 0, 0, 1])
    """Цвет ползунка в выключенном состоянии (красный)."""
    
    track_color_active = ColorProperty([0.15, 0.3, 0.15, 1])
    """Цвет фона во включенном состоянии."""
    
    track_color_inactive = ColorProperty([0.2, 0.1, 0.1, 1])
    """Цвет фона в выключенном состоянии."""
    
    thumb_padding = NumericProperty(4)
    """Отступ ползунка от краев."""
    
    # Внутренние атрибуты
    _track = None
    _thumb = None
    _track_color = None
    _thumb_color = None
    
    def __init__(self, **kwargs):
        # Устанавливаем настройки по умолчанию для AnchorLayout
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        self.size_hint = (None, None)
        
        # Устанавливаем размеры из kwargs или значения по умолчанию
        self.size = kwargs.pop('size', (64, 36))
        
        # Устанавливаем цвета из kwargs или значения по умолчанию
        self.thumb_color_active = kwargs.pop('thumb_color_active', [0.1, 0.5, 0.8, 1]) # цвет ползунка в включенном состоянии
        self.track_color_active = kwargs.pop('track_color_active', [0.05, 0.25, 0.4, 1]) # цвет фона в включенном состоянии
        self.thumb_color_inactive = kwargs.pop('thumb_color_inactive', [0.8, 0.2, 0.2, 1]) # цвет ползунка в выключенном состоянии
        self.track_color_inactive = kwargs.pop('track_color_inactive', [0.2, 0.1, 0.1, 1]) # цвет фона в выключенном состоянии
        
        # Устанавливаем начальный цвет ползунка в зависимости от состояния active
        if 'active' in kwargs and kwargs['active']:
            self.thumb_color = self.thumb_color_active
            self.active = True
        else:
            self.thumb_color = self.thumb_color_inactive
            self.active = kwargs.get('active', False)
        
        # Инициализируем AnchorLayout
        super().__init__(**kwargs)
        
        # Инициализируем графику
        self._init_graphics()
        
        # Привязываем обработчики изменений
        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics,
            active=self._update_state
        )
        
        # Принудительно обновляем графику после инициализации
        Clock.schedule_once(self._update_graphics, 0.1)
        
    def _init_graphics(self):
        """Инициализация графических элементов."""
        with self.canvas:
            # Фон (трек)
            self._track_color = Color(*self.track_color_active if self.active else self.track_color_inactive)
            self._track = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.height/2,]
            )
            
            # Ползунок (thumb)
            self._thumb_color = Color(*self.thumb_color_active if self.active else self.thumb_color_inactive)
            self._thumb = RoundedRectangle(
                pos=(0, 0),  # Временная позиция, обновится в _update_graphics
                size=(self.height - 2*self.thumb_padding, self.height - 2*self.thumb_padding),
                radius=[(self.height - 2*self.thumb_padding)/2,]
            )
    

    
    def _update_graphics(self, *args):
        """Обновляет графические элементы при изменении размера/позиции."""
        if None in (self._track, self._thumb):
            return
        
        # Обновляем трек
        self._track.pos = self.pos
        self._track.size = self.size
        self._track.radius = [self.height/2,]
        
        # Обновляем ползунок
        thumb_size = self.height - 2 * self.thumb_padding
        self._thumb.size = (thumb_size, thumb_size)
        self._thumb.radius = [thumb_size/2,]
        
        # Вычисляем позицию ползунка
        if self.active:
            # Позиция справа (включено)
            thumb_x = self.x + self.width - thumb_size - self.thumb_padding
        else:
            # Позиция слева (выключено)
            thumb_x = self.x + self.thumb_padding
        
        thumb_y = self.y + self.thumb_padding
        self._thumb.pos = (thumb_x, thumb_y)
        
        # Обновляем цвета
        if self.active:
            self._track_color.rgba = self.track_color_active
            self._thumb_color.rgba = self.thumb_color_active
        else:
            self._track_color.rgba = self.track_color_inactive
            self._thumb_color.rgba = self.thumb_color_inactive
    
    def _update_state(self, *args):
        """Обновляет состояние переключателя с анимацией."""
        if None in (self._track, self._thumb, self._track_color, self._thumb_color):
            return
            
        try:
            # Анимация движения ползунка
            thumb_size = self.height - 2 * self.thumb_padding
            if self.active:
                # Позиция справа (включено)
                target_x = self.x + self.width - thumb_size - self.thumb_padding
            else:
                # Позиция слева (выключено)
                target_x = self.x + self.thumb_padding
            
            target_y = self.y + self.thumb_padding
            
            # Создаем анимацию позиции
            anim = Animation(
                pos=(target_x, target_y),
                d=0.2,
                t='out_quad'
            )
            
            # Запускаем анимацию
            anim.start(self._thumb)
            
            # Обновляем цвета
            self._update_graphics()
            
        except Exception as e:
            print(f"Ошибка при обновлении состояния переключателя: {e}")
            # В случае ошибки все равно обновляем графику
            self._update_graphics()
    
    def on_touch_down(self, touch):
        """Обработчик нажатия на переключатель."""
        if self.collide_point(*touch.pos):
            self.active = not self.active
            return True
        return super().on_touch_down(touch)
    
    def on_active(self, instance, value):
        """Обработчик изменения свойства active."""
        # Обновляем состояние при программном изменении свойства active
        # Проверяем, что графические элементы инициализированы
        if None not in (self._track, self._thumb, self._track_color, self._thumb_color):
            self._update_state()
