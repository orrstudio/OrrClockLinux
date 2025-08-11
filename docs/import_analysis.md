# Анализ импортов проекта OrrClockLinux

## main.py

### Необходимые импорты:
```python
import os
import kivy
from datetime import datetime
import math
from kivy.animation import Animation
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from ui.settings_window import SettingsWindow
from ui.settings_manager import SettingsManager
from ui.clock_widget import ClockWidget
from data.database import SettingsDatabase
from logic.clock_functions import get_formatted_time
from ui.main_portrait import create_portrait_widgets
from ui.main_landscape import create_landscape_prayer_times_table
from ui.main_square import create_square_prayer_times_table
from logic.display_utils import is_mobile_device
from logic.fonts_registration import register_fonts
from logic.prayer_time_calculator import prayer_time_calculator
from logic.hijri_date import hijri_date_manager
from logic.midnight_update_manager import MidnightUpdateManager
from logic.prayer_times import prayer_times_manager
from utils.logger import logger
```

### Неиспользуемые импорты:
- `from kivy.input.motionevent import MotionEvent`
- `from kivy.metrics import sp` (импортирован, но не используется)

### Примечание:
- `from kivy.animation import Animation` используется в методе `stop_clock_animation` для отмены анимации прозрачности у `title_label`.

## utils/logger.py

### Необходимые импорты:
```python
import sys
import builtins
from typing import Optional, Any
```

### Неиспользуемые импорты:
Отсутствуют

## data/database.py

### Необходимые импорты:
```python
from pathlib import Path
import sqlite3
from kivy.core.window import Window
```

### Неиспользуемые импорты:
- `from logic.display_utils import is_mobile_device, find_current_monitor, get_monitor_info`
  (используется только `is_mobile_device`)

## ui/settings_window.py

### Необходимые импорты:
```python
import logging
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from ui.settings_color import ColorButton
from data.database import SettingsDatabase
from logic.display_utils import is_mobile_device
```

### Неиспользуемые импорты:
- `from kivy.uix.dropdown import DropDown`
- `from kivy.uix.popup import Popup`
- `from kivy.uix.spinner import Spinner` (если не используется в коде)

## Рекомендации по оптимизации:

1. Удалить неиспользуемые импорты во всех файлах

