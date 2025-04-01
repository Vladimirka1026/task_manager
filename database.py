# -*- coding: utf-8 -*-
"""
Менеджер базы данных.
Управляет операциями с базой данных SQLite.
"""

import sqlite3
import logging
import traceback
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Класс для управления базой данных."""
    
    def __init__(self):
        """Инициализация менеджера базы данных."""
        try:
            logger.debug("Подключение к базе данных")
            self.conn = sqlite3.connect("tasks.db")
            self.cursor = self.conn.cursor()
            self.init_db()
            logger.debug("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def init_db(self):
        """Инициализация структуры базы данных."""
        try:
            # Создаем таблицу tasks если она не существует
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER DEFAULT 1,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Проверяем наличие колонок
            self.cursor.execute("PRAGMA table_info(tasks)")
            columns = [column[1] for column in self.cursor.fetchall()]
            if 'priority' not in columns:
                self.cursor.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 1")
            if 'completed' not in columns:
                self.cursor.execute("ALTER TABLE tasks ADD COLUMN completed BOOLEAN DEFAULT 0")
            
            self.conn.commit()
            logger.debug("Структура базы данных проверена")
        except Exception as e:
            logger.error(f"Ошибка при инициализации структуры БД: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def get_all_tasks(self):
        """Получение всех задач из базы данных."""
        try:
            self.cursor.execute("""
                SELECT id, title, description, priority, completed, created_at, updated_at
                FROM tasks 
                ORDER BY id
            """)
            tasks = self.cursor.fetchall()
            logger.debug(f"Получено {len(tasks)} задач")
            return tasks
        except Exception as e:
            logger.error(f"Ошибка при получении задач: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def add_task(self, title, description):
        """Добавление новой задачи."""
        try:
            self.cursor.execute("""
                INSERT INTO tasks (title, description, priority, completed, created_at, updated_at)
                VALUES (?, ?, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (title, description))
            self.conn.commit()
            logger.debug(f"Добавлена задача: {title}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении задачи: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def update_task(self, task_id, title, description):
        """Обновление существующей задачи."""
        try:
            self.cursor.execute("""
                UPDATE tasks 
                SET title=?, description=?, updated_at=CURRENT_TIMESTAMP 
                WHERE id=?
            """, (title, description, task_id))
            self.conn.commit()
            logger.debug(f"Обновлена задача {task_id}: {title}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении задачи: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def delete_tasks(self, task_ids):
        """Удаление задач по их ID."""
        try:
            placeholders = ",".join("?" * len(task_ids))
            self.cursor.execute(f"""
                DELETE FROM tasks 
                WHERE id IN ({placeholders})
            """, task_ids)
            self.conn.commit()
            logger.debug(f"Удалено задач: {len(task_ids)}")
        except Exception as e:
            logger.error(f"Ошибка при удалении задач: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def update_task_priority(self, task_ids, new_priority):
        """Изменение приоритета задач."""
        try:
            placeholders = ",".join("?" * len(task_ids))
            self.cursor.execute(f"""
                UPDATE tasks 
                SET priority = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id IN ({placeholders})
            """, [new_priority] + task_ids)
            self.conn.commit()
            logger.debug(f"Обновлен приоритет {len(task_ids)} задач")
        except Exception as e:
            logger.error(f"Ошибка при изменении приоритета задач: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def toggle_task_status(self, task_ids, new_status):
        """Изменение статуса выполнения задач."""
        try:
            placeholders = ",".join("?" * len(task_ids))
            self.cursor.execute(f"""
                UPDATE tasks 
                SET completed = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id IN ({placeholders})
            """, [new_status] + task_ids)
            self.conn.commit()
            logger.debug(f"Обновлен статус {len(task_ids)} задач")
        except Exception as e:
            logger.error(f"Ошибка при изменении статуса задач: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def close(self):
        """Закрытие соединения с базой данных."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                logger.debug("Соединение с базой данных закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с БД: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def clear_tasks(self):
        """Очистка всех задач из базы данных."""
        try:
            # Удаляем все задачи
            self.cursor.execute("DELETE FROM tasks")
            
            # Сбрасываем автоинкремент ID
            self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
            
            self.conn.commit()
            logger.debug("Все задачи удалены, счетчик ID сброшен")
        except Exception as e:
            logger.error(f"Ошибка при очистке задач: {str(e)}")
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise 
    
    def reorder_tasks(self, tasks):
        """Обновление порядка задач в базе данных."""
        try:
            # Начинаем транзакцию
            self.conn.execute("BEGIN TRANSACTION")
            
            # Обновляем данные для каждой задачи
            for task in tasks:
                self.cursor.execute("""
                    UPDATE tasks 
                    SET title = ?,
                        description = ?,
                        priority = ?,
                        completed = ?,
                        updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (task[1], task[2], task[3], task[4], task[0]))
            
            # Завершаем транзакцию
            self.conn.commit()
            logger.debug("Порядок и данные задач обновлены")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении порядка задач: {str(e)}")
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise 