# -*- coding: utf-8 -*-
"""
Менеджер задач - простое приложение для управления списком задач.
Функциональность:
- Добавление, редактирование и удаление задач
- Сохранение задач в базе данных SQLite
- Сохранение настроек окна
- Поддержка горячих клавиш
"""

import sys
import traceback
import logging
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from database import DatabaseManager
from settings import SettingsManager
from ui_manager import UIManager
from sound_manager import SoundManager
from edit_task import EditTaskDialog

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskManager(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        """Инициализация главного окна приложения."""
        try:
            logger.debug("Инициализация TaskManager")
            super().__init__()
            
            # Инициализация менеджеров
            self.db_manager = DatabaseManager()
            self.settings_manager = SettingsManager()
            self.ui_manager = UIManager(self)
            self.sound_manager = SoundManager()
            
            # Устанавливаем заголовок окна
            self.setWindowTitle("Менеджер задач")
            
            # Настройка меню
            self.setup_menu()
            
            # Загрузка настроек
            self.settings_manager.load_window_geometry(self)
            
            # Загрузка стилей
            self.ui_manager.load_styles()
            
            # Загрузка задач
            self.load_tasks()
            
            # Подключение сигналов
            self.setup_connections()
            
            logger.debug("Инициализация завершена успешно")
        except Exception as e:
            logger.error(f"Ошибка в инициализации TaskManager: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def setup_menu(self):
        """Настройка меню приложения."""
        try:
            # Создаем меню "Файл"
            file_menu = self.menuBar().addMenu("Файл")
            
            # Добавляем действия в меню
            self.addAction = QAction("Добавить задачу", self)
            self.addAction.setShortcut("Ctrl+N")
            self.editAction = QAction("Редактировать задачу", self)
            self.editAction.setShortcut("Ctrl+E")
            self.deleteAction = QAction("Удалить задачу", self)
            self.deleteAction.setShortcut("Delete")
            self.completeAction = QAction("Отметить как выполненную", self)
            self.completeAction.setShortcut("Ctrl+D")
            self.increasePriorityAction = QAction("Увеличить приоритет", self)
            self.increasePriorityAction.setShortcut("Ctrl+Up")
            self.decreasePriorityAction = QAction("Уменьшить приоритет", self)
            self.decreasePriorityAction.setShortcut("Ctrl+Down")
            
            # Добавляем действия в меню
            file_menu.addAction(self.addAction)
            file_menu.addAction(self.editAction)
            file_menu.addAction(self.deleteAction)
            file_menu.addAction(self.completeAction)
            file_menu.addSeparator()
            file_menu.addAction(self.increasePriorityAction)
            file_menu.addAction(self.decreasePriorityAction)
            file_menu.addSeparator()
            
            # Добавляем действие выхода
            exit_action = QAction("Выход", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            logger.debug("Меню настроено успешно")
        except Exception as e:
            logger.error(f"Ошибка при настройке меню: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def setup_connections(self):
        """Настройка подключений сигналов и слотов."""
        try:
            # Подключаем сигналы кнопок
            self.ui_manager.addButton.clicked.connect(self.add_task)
            self.ui_manager.editButton.clicked.connect(self.edit_task)
            self.ui_manager.deleteButton.clicked.connect(self.delete_task)
            self.ui_manager.completeButton.clicked.connect(self.toggle_task_status)
            self.ui_manager.clearButton.clicked.connect(self.clear_tasks)
            
            # Подключаем сигнал переупорядочивания
            self.ui_manager.taskTable.model().rowsMoved.connect(self.handle_task_reorder)
            
            # Подключаем сигнал изменения ячейки
            self.ui_manager.taskTable.itemChanged.connect(self.handle_cell_changed)
            
            # Подключаем горячие клавиши
            self.completeAction.triggered.connect(self.toggle_task_status)
            self.increasePriorityAction.triggered.connect(self.increase_priority)
            self.decreasePriorityAction.triggered.connect(self.decrease_priority)
            
            logger.debug("Подключения сигналов настроены")
        except Exception as e:
            logger.error(f"Ошибка при настройке подключений: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def load_tasks(self):
        """Загрузка задач из базы данных."""
        try:
            tasks = self.db_manager.get_all_tasks()
            self.ui_manager.load_tasks(tasks)
            self.statusBar().showMessage("Готово")
        except Exception as e:
            logger.error(f"Ошибка при загрузке задач: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def add_task(self):
        """Добавление новой задачи."""
        try:
            dialog = EditTaskDialog(self)
            dialog.setWindowTitle("Добавить задачу")
            if dialog.exec():
                title, desc = dialog.get_data()
                self.db_manager.add_task(title, desc)
                self.load_tasks()
                self.statusBar().showMessage(f"Задача '{title}' добавлена", 3000)
        except Exception as e:
            logger.error(f"Ошибка при добавлении задачи: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить задачу: {str(e)}")
    
    def edit_task(self):
        """Редактирование существующей задачи."""
        try:
            task = self.ui_manager.get_current_task()
            if not task:
                QMessageBox.warning(self, "Предупреждение", "Выберите задачу для редактирования")
                return
            
            dialog = EditTaskDialog(self, task['title'], task['description'])
            dialog.setWindowTitle("Редактировать задачу")
            if dialog.exec():
                new_title, new_desc = dialog.get_data()
                self.db_manager.update_task(task['id'], new_title, new_desc)
                self.load_tasks()
                self.statusBar().showMessage(f"Задача '{new_title}' обновлена", 3000)
        except Exception as e:
            logger.error(f"Ошибка при редактировании задачи: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось отредактировать задачу: {str(e)}")
    
    def delete_task(self):
        """Удаление выбранных задач."""
        try:
            task_ids = self.ui_manager.get_selected_task_ids()
            if not task_ids:
                QMessageBox.warning(self, "Предупреждение", "Выберите задачи для удаления")
                return
            
            task_titles = self.ui_manager.get_selected_task_titles()
            tasks_str = "\n".join([f"- {title}" for title in task_titles])
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение", 
                f"Вы уверены, что хотите удалить следующие задачи?\n{tasks_str}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.delete_tasks(task_ids)
                self.load_tasks()
                self.statusBar().showMessage(f"Удалено задач: {len(task_ids)}", 3000)
        except Exception as e:
            logger.error(f"Ошибка при удалении задач: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачи: {str(e)}")
    
    def toggle_task_status(self):
        """Переключение статуса выполнения для выбранных задач."""
        try:
            task_ids = self.ui_manager.get_selected_task_ids()
            if not task_ids:
                QMessageBox.warning(self, "Предупреждение", "Выберите задачи")
                return
            
            # Получаем текущий статус первой задачи и применяем противоположный ко всем
            current_row = self.ui_manager.taskTable.currentRow()
            current_status = self.ui_manager.taskTable.item(current_row, 4).text() == "Выполнено"
            new_status = not current_status
            
            self.db_manager.toggle_task_status(task_ids, new_status)
            
            # Воспроизводим звук завершения
            self.sound_manager.play_complete()
            
            # Обновляем отображение
            self.load_tasks()
            self.statusBar().showMessage(f"Обновлено задач: {len(task_ids)}", 3000)
        except Exception as e:
            logger.error(f"Ошибка при изменении статуса задач: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус задач: {str(e)}")
    
    def increase_priority(self):
        """Увеличение приоритета выбранных задач."""
        try:
            task_ids = self.ui_manager.get_selected_task_ids()
            if not task_ids:
                QMessageBox.warning(self, "Предупреждение", "Выберите задачи")
                return
            
            # Получаем текущий приоритет первой задачи и увеличиваем его
            current_priority = int(self.ui_manager.taskTable.item(self.ui_manager.taskTable.currentRow(), 3).text())
            new_priority = min(current_priority + 1, 4)  # Максимальный приоритет 4
            
            self.db_manager.update_task_priority(task_ids, new_priority)
            
            # Воспроизводим звук
            self.sound_manager.play_click()
            
            # Обновляем отображение
            self.load_tasks()
            self.statusBar().showMessage(f"Приоритет увеличен до {new_priority}", 3000)
        except Exception as e:
            logger.error(f"Ошибка при увеличении приоритета: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить приоритет: {str(e)}")
    
    def decrease_priority(self):
        """Уменьшение приоритета выбранных задач."""
        try:
            task_ids = self.ui_manager.get_selected_task_ids()
            if not task_ids:
                QMessageBox.warning(self, "Предупреждение", "Выберите задачи")
                return
            
            # Получаем текущий приоритет первой задачи и уменьшаем его
            current_priority = int(self.ui_manager.taskTable.item(self.ui_manager.taskTable.currentRow(), 3).text())
            new_priority = max(current_priority - 1, 1)  # Минимальный приоритет 1
            
            self.db_manager.update_task_priority(task_ids, new_priority)
            
            # Воспроизводим звук
            self.sound_manager.play_click()
            
            # Обновляем отображение
            self.load_tasks()
            self.statusBar().showMessage(f"Приоритет уменьшен до {new_priority}", 3000)
        except Exception as e:
            logger.error(f"Ошибка при уменьшении приоритета: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить приоритет: {str(e)}")
    
    def handle_task_reorder(self, parent, start, end, destination, row):
        """Обработка переупорядочивания задач."""
        try:
            # Блокируем сигналы таблицы, чтобы избежать рекурсивных вызовов
            self.ui_manager.taskTable.blockSignals(True)
            
            # Получаем ID задач
            source_id = int(self.ui_manager.taskTable.item(start, 0).text())
            target_id = int(self.ui_manager.taskTable.item(row, 0).text())
            
            # Обновляем порядок в базе данных
            self.db_manager.reorder_tasks(source_id, target_id)
            
            # Перезагружаем данные из базы
            self.load_tasks()
            
            # Воспроизводим звук
            self.sound_manager.play_click()
            
            logger.debug(f"Задачи переупорядочены: {source_id} -> {target_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при переупорядочивании задач: {str(e)}")
            logger.error(traceback.format_exc())
            # Восстанавливаем исходное состояние таблицы
            self.load_tasks()
        finally:
            # Разблокируем сигналы таблицы
            self.ui_manager.taskTable.blockSignals(False)
    
    def handle_cell_changed(self, item):
        """Обработка изменения ячейки в таблице."""
        try:
            # Блокируем сигналы, чтобы избежать рекурсии
            self.ui_manager.taskTable.blockSignals(True)
            
            # Получаем ID задачи из данных первой ячейки строки
            task_id = self.ui_manager.taskTable.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
            
            # Проверяем, что изменилась ячейка с приоритетом (колонка 2)
            if item.column() == 2:
                try:
                    # Пытаемся преобразовать новое значение в число
                    new_priority = int(item.text())
                    
                    # Проверяем, что приоритет в допустимом диапазоне
                    if 1 <= new_priority <= 4:
                        # Обновляем приоритет в базе данных
                        self.db_manager.update_task_priority([task_id], new_priority)
                        # Воспроизводим звук
                        self.sound_manager.play_click()
                        # Обновляем только цвет и флаги ячейки
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        # Если приоритет вне диапазона, возвращаем старое значение
                        tasks = self.db_manager.get_all_tasks()
                        old_priority = next(task[3] for task in tasks if task[0] == task_id)
                        item.setText(str(old_priority))
                        self.show_warning("Приоритет должен быть от 1 до 4")
                except ValueError:
                    # Если введено не число, возвращаем старое значение
                    tasks = self.db_manager.get_all_tasks()
                    old_priority = next(task[3] for task in tasks if task[0] == task_id)
                    item.setText(str(old_priority))
                    self.show_warning("Приоритет должен быть числом от 1 до 4")
                    
        except Exception as e:
            logger.error(f"Ошибка при обработке изменения ячейки: {str(e)}")
            logger.error(traceback.format_exc())
            # Перезагружаем задачи только в случае серьезной ошибки
            self.load_tasks()
        finally:
            # Разблокируем сигналы
            self.ui_manager.taskTable.blockSignals(False)
    
    def clear_tasks(self):
        """Очистка всех задач."""
        try:
            reply = QMessageBox.question(
                self, 
                "Подтверждение", 
                "Вы уверены, что хотите удалить все задачи?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.clear_tasks()
                self.load_tasks()
                self.statusBar().showMessage("Список задач очищен", 3000)
        except Exception as e:
            logger.error(f"Ошибка при очистке задач: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Не удалось очистить список задач: {str(e)}")
    
    def closeEvent(self, event):
        """Обработка события закрытия приложения."""
        try:
            self.settings_manager.save_window_geometry(self)
            self.db_manager.close()
            logger.debug("Приложение закрыто успешно")
            event.accept()
        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {str(e)}")
            logger.error(traceback.format_exc())
            event.accept()

if __name__ == "__main__":
    try:
        logger.debug("Запуск приложения")
        app = QApplication(sys.argv)
        window = TaskManager()
        window.show()
        logger.debug("Главное окно отображено")
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске приложения: {str(e)}")
        logger.error(traceback.format_exc())
        raise
