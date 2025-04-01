# -*- coding: utf-8 -*-
"""
Менеджер звуковых эффектов.
Управляет воспроизведением звуков при различных действиях в приложении.
"""

import winsound
import logging
import traceback

# Настройка логирования
logger = logging.getLogger(__name__)

class SoundManager:
    """Класс для управления звуковыми эффектами."""
    
    def __init__(self):
        """Инициализация менеджера звуков."""
        try:
            logger.debug("Инициализация менеджера звуков")
        except Exception as e:
            logger.error(f"Ошибка при инициализации звуковых эффектов: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def play_click(self):
        """Воспроизводит звук клика."""
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            logger.debug("Воспроизведен звук клика")
        except Exception as e:
            logger.error(f"Ошибка при воспроизведении звука клика: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def play_complete(self):
        """Воспроизводит звук завершения."""
        try:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            logger.debug("Воспроизведен звук завершения")
        except Exception as e:
            logger.error(f"Ошибка при воспроизведении звука завершения: {str(e)}")
            logger.error(traceback.format_exc())
            raise 