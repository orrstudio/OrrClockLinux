"""
Базовые компоненты для настроек приложения.

Этот пакет содержит базовые классы виджетов, используемые в настройках приложения.
"""

from .responsive_label import ResponsiveLabel
from .settings_card import SettingsCard
from .settings_section import SettingsSection
from ui.components.custom_button import CustomButton

__all__ = [
    'ResponsiveLabel',
    'SettingsCard',
    'SettingsSection',
    'CustomButton',
]
