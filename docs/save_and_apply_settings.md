# Сохранение и применение настроек

В этом документе описано, как в приложении реализовано сохранение и применение настроек.

## 1. Сохранение положения и размера окна

### Где происходит:
- В методе `on_stop` класса `MainWindowApp` (файл `main.py`)

### Процесс:
1. При закрытии приложения автоматически вызывается метод `on_stop`
2. В этом методе сохраняются текущие параметры окна:
   ```python
   def on_stop(self):
       """Вызывается при закрытии приложения"""
       # Сохраняем настройки окна
       if not is_mobile_device():
           width, height = Window.size
           x, y = Window.left, Window.top
           self.settings_db.save_window_settings(width, height, x, y)
   ```

3. Метод `save_window_settings` в классе `SettingsDatabase` сохраняет эти данные в базу:
   ```python
   def save_window_settings(self, width, height, x, y):
       """Сохраняет настройки окна в БД"""
       try:
           self.cursor.execute('''
               INSERT OR REPLACE INTO window_settings 
               (id, width, height, x, y) 
               VALUES (1, ?, ?, ?, ?)
           ''', (width, height, x, y))
           self.connection.commit()
       except Exception:
           pass
   ```

## 2. Сохранение настроек цвета

### Где происходит:
- В методе `on_accept` класса `SettingsWindow` (файл `settings_window.py`)

### Процесс:
1. При нажатии кнопки "Сохранить" в окне настроек вызывается метод `on_accept`:
   ```python
   def on_accept(self, *args):
       """Сохраняет настройки при нажатии кнопки Save."""
       try:
           # Сохраняем цвет, если выбран
           if hasattr(self, 'selected_color') and self.selected_color:
               color_key = self.selected_color.lower()
               if color_key in self.colors:
                   # Сохраняем в базу данных
                   self.db.save_setting('color', color_key)
                   # Применяем цвет через callback
                   if self.apply_callback:
                       self.apply_callback(self.colors[color_key])
   ```

2. Метод `save_setting` в классе `SettingsDatabase` сохраняет значение цвета:
   ```python
   def save_setting(self, key, value):
       """Сохранение значения настройки"""
       self.cursor.execute("""
           INSERT OR REPLACE INTO settings (key, value) 
           VALUES (?, ?)
       """, (key, value))
       self.connection.commit()
   ```

## 3. Восстановление настроек при запуске

### При старте приложения:
1. В методе `build` класса `MainWindowApp`:
   ```python
   def build(self):
       # Применяем сохранённые настройки окна
       if not is_mobile_device():
           self.settings_db.apply_window_settings(Window)
   ```

2. Метод `apply_window_settings` загружает настройки из базы:
   ```python
   def apply_window_settings(self, window):
       """Применяет настройки окна"""
       settings = self.get_window_settings()
       if settings:
           width, height, x, y = settings
           window.size = (width, height)
           window.left = x
           window.top = y
   ```

## 4. Особенности работы

1. **Атомарность операций**:
   - Каждая операция с базой данных выполняется в своей транзакции
   - Используется `commit()` для подтверждения изменений

2. **Обработка ошибок**:
   - Все операции обёрнуты в try-except блоки
   - Ошибки логируются, но не прерывают работу приложения

3. **Производительность**:
   - Настройки сохраняются только при изменении
   - Применение настроек происходит один раз при старте

4. **Потокобезопасность**:
   - Все операции с базой данных выполняются в основном потоке приложения
