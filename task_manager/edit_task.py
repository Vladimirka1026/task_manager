# -*- coding: utf-8 -*-
"""
Диалоговое окно для создания и редактирования задач.
"""

import logging
import traceback
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox

# Настройка логирования
logger = logging.getLogger(__name__)

class EditTaskDialog(QDialog):
    """Диалоговое окно для создания и редактирования задач."""
    
    def __init__(self, parent=None, title="", description=""):
        """
        Инициализация диалогового окна.
        
        Args:
            parent: Родительский виджет
            title: Заголовок задачи
            description: Описание задачи
        """
        try:
            logger.debug("Инициализация диалога редактирования")
            super().__init__(parent)
            
            # Настройка окна
            self.setWindowTitle("Редактировать задачу")
            self.setModal(True)
            self.setMinimumWidth(400)
            
            # Создание виджетов
            self.setup_ui()
            
            # Заполнение полей
            self.titleEdit.setText(title)
            self.descEdit.setPlainText(description)
            
            logger.debug(f"Заполнены поля: title='{title}', description='{description}'")
            
        except Exception as e:
            logger.error(f"Ошибка в инициализации диалога: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        try:
            # Создаем главный layout
            layout = QVBoxLayout(self)
            
            # Поле для заголовка
            title_layout = QHBoxLayout()
            title_label = QLabel("Заголовок:")
            self.titleEdit = QLineEdit()
            title_layout.addWidget(title_label)
            title_layout.addWidget(self.titleEdit)
            layout.addLayout(title_layout)
            
            # Поле для описания
            desc_label = QLabel("Описание:")
            self.descEdit = QTextEdit()
            layout.addWidget(desc_label)
            layout.addWidget(self.descEdit)
            
            # Кнопки
            button_layout = QHBoxLayout()
            self.saveButton = QPushButton("Сохранить")
            self.cancelButton = QPushButton("Отмена")
            
            self.saveButton.clicked.connect(self.validate_and_accept)
            self.cancelButton.clicked.connect(self.reject)
            
            button_layout.addWidget(self.saveButton)
            button_layout.addWidget(self.cancelButton)
            layout.addLayout(button_layout)
            
            logger.debug("UI диалога настроен")
            
        except Exception as e:
            logger.error(f"Ошибка при настройке UI: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def validate_and_accept(self):
        """Проверяет данные перед сохранением."""
        try:
            title = self.titleEdit.text().strip()
            if not title:
                QMessageBox.warning(self, "Ошибка", "Заголовок задачи не может быть пустым")
                return
            self.accept()
            logger.debug("Данные валидированы и приняты")
        except Exception as e:
            logger.error(f"Ошибка при валидации данных: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def get_data(self):
        """
        Возвращает данные из полей ввода.
        
        Returns:
            tuple: (заголовок, описание)
        """
        try:
            title = self.titleEdit.text().strip()
            desc = self.descEdit.toPlainText().strip()
            logger.debug(f"Получены данные из диалога: title='{title}', description='{desc}'")
            return title, desc
        except Exception as e:
            logger.error(f"Ошибка при получении данных из диалога: {str(e)}")
            logger.error(traceback.format_exc())
            raise
