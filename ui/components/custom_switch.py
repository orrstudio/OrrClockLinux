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
    """Текущий цвет ползунка переключателя."""
    
    thumb_color_active = ColorProperty([0, 1, 0, 1])
    """Цвет ползунка во включенном состоянии."""
    
    thumb_color_inactive = ColorProperty([1, 0, 0, 1])
    """Цвет ползунка в выключенном состоянии."""
    
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
        
        # Инициализируем AnchorLayout
        super().__init__(**kwargs)
        
        # Инициализируем графику
        self._init_graphics()
        
        # Привязываем обработчики изменений после инициализации графики
        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics
        )
        
        # Откладываем привязку active, чтобы избежать преждевременного вызова _update_state
        Clock.schedule_once(lambda dt: self.bind(active=self._update_state))
    
    def _init_graphics(self):
        """Инициализация графических элементов."""
        with self.canvas:
            # Фон (трек)
            self._track_color = Color(*self.track_color_inactive)
            self._track = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.height/2,]
            )
            
            # Ползунок (thumb)
            self._thumb_color = Color(*self.thumb_color)
            self._thumb = RoundedRectangle(
                pos=self._get_thumb_pos(),
                size=(self.height - 2*self.thumb_padding, self.height - 2*self.thumb_padding),
                radius=[(self.height - 2*self.thumb_padding)/2,]
            )
    
    def _get_thumb_pos(self):
        """Возвращает позицию ползунка в зависимости от состояния."""
        if self.active:
            return (self.right - self.height + self.thumb_padding, self.y + self.thumb_padding)
        return (self.x + self.thumb_padding, self.y + self.thumb_padding)
    
    def _update_graphics(self, *args):
        """Обновляет графические элементы при изменении размера/позиции."""
        if None in (self._track, self._thumb):
            return
            
        self._track.pos = self.pos
        self._track.size = self.size
        self._thumb.pos = self._get_thumb_pos()
        self._track.radius = [self.height/2,]
        self._thumb.radius = [(self.height - 2*self.thumb_padding)/2,]
    
    def _update_state(self, *args):
        """Обновляет состояние переключателя с анимацией."""
        # Проверяем, что графические элементы инициализированы
        if None in (self._track, self._thumb, self._track_color, self._thumb_color):
            return
            
        try:
            # Анимация движения ползунка
            anim = Animation(
                pos=self._get_thumb_pos(),
                d=0.2,
                t='out_quad'
            )
            
            # Обновление цветов в зависимости от состояния
            if self.active:
                self._track_color.rgba = self.track_color_active
                self._thumb_color.rgba = self.thumb_color_active
            else:
                self._track_color.rgba = self.track_color_inactive
                self._thumb_color.rgba = self.thumb_color_inactive
            
            anim.start(self._thumb)
        except Exception as e:
            print(f"Ошибка при обновлении состояния переключателя: {e}")
    
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
