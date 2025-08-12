from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import StringProperty

class ResponsiveLabel(Label):
    """
    Адаптивная метка, которая автоматически подстраивает размер текста и переносит его.
    """
    
    text_language = StringProperty('ru')
    """Язык текста для правильного отображения (по умолчанию: 'ru')."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1])
        )
        self.halign = 'left'
        self.valign = 'middle'
        self.padding = (dp(5), dp(5))
        self.text_size = (None, None)
        self.size_hint = (1/3, None)
        self.height = dp(40)
        self.color = (1, 1, 1, 1)
        self.text_language = 'ru'
        self.line_height = 1.2
