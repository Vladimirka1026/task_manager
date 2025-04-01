from PyQt6.QtCore import QSettings
import logging

logger = logging.getLogger(__name__)

class SettingsManager:
    """Класс для управления настройками приложения."""
    
    def __init__(self, company="MyCompany", app_name="Менеджер задач"):
        self.settings = QSettings(company, app_name)
        logger.debug("Менеджер настроек инициализирован")
    
    def save_window_geometry(self, window):
        """Сохранение геометрии окна."""
        try:
            self.settings.setValue("size", window.size())
            self.settings.setValue("pos", window.pos())
            logger.debug("Геометрия окна сохранена")
        except Exception as e:
            logger.error(f"Ошибка при сохранении геометрии окна: {str(e)}")
    
    def load_window_geometry(self, window):
        """Загрузка геометрии окна."""
        try:
            window.resize(self.settings.value("size", window.size()))
            window.move(self.settings.value("pos", window.pos()))
            logger.debug("Геометрия окна загружена")
        except Exception as e:
            logger.error(f"Ошибка при загрузке геометрии окна: {str(e)}")
    
    def save_theme(self, is_dark):
        """Сохранение темы."""
        try:
            self.settings.setValue("dark_theme", is_dark)
            logger.debug(f"Тема сохранена: {'темная' if is_dark else 'светлая'}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении темы: {str(e)}")
    
    def load_theme(self):
        """Загрузка темы."""
        try:
            return self.settings.value("dark_theme", False, type=bool)
        except Exception as e:
            logger.error(f"Ошибка при загрузке темы: {str(e)}")
            return False
    
    def save_sound_enabled(self, enabled):
        """Сохранение настройки звука."""
        try:
            self.settings.setValue("sound_enabled", enabled)
            logger.debug(f"Настройка звука сохранена: {'включен' if enabled else 'выключен'}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении настройки звука: {str(e)}")
    
    def load_sound_enabled(self):
        """Загрузка настройки звука."""
        try:
            return self.settings.value("sound_enabled", True, type=bool)
        except Exception as e:
            logger.error(f"Ошибка при загрузке настройки звука: {str(e)}")
            return True 