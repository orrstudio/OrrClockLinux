"""
Модуль для работы с настройками приложения.

Этот пакет содержит компоненты для настройки различных аспектов приложения,
разделенные на логические блоки.
"""

# Импортируем базовые компоненты
from .base import (
    ResponsiveLabel,
    SettingsCard,
    SettingsSection,
    CustomButton
)

__all__ = [
    'ResponsiveLabel',
    'SettingsCard',
    'SettingsSection',
    'CustomButton',
]
