from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QHeaderView, QPushButton, QTableWidgetItem)
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt
import logging
import os
import winreg
import traceback

logger = logging.getLogger(__name__)

class UIManager:
    """Класс для управления пользовательским интерфейсом."""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        logger.debug("UI менеджер инициализирован")
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        try:
            # Создаем центральный виджет
            central_widget = QWidget()
            self.parent.setCentralWidget(central_widget)
            
            # Создаем главный layout
            layout = QVBoxLayout(central_widget)
            
            # Создаем таблицу задач
            self.taskTable = QTableWidget()
            self.taskTable.setColumnCount(4)
            self.taskTable.setHorizontalHeaderLabels(["Заголовок", "Описание", "Приоритет", "Статус"])
            self.taskTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.taskTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.taskTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.taskTable.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
            
            # Включаем поддержку drag-and-drop
            self.taskTable.setDragEnabled(True)
            self.taskTable.setDragDropMode(QTableWidget.DragDropMode.InternalMove)
            self.taskTable.setDragDropOverwriteMode(False)
            
            # Подключаем обработчики событий drag-and-drop
            self.taskTable.dragEnterEvent = self.handle_drag_enter
            self.taskTable.dragMoveEvent = self.handle_drag_move
            self.taskTable.dropEvent = self.handle_drop_event
            
            layout.addWidget(self.taskTable)
            
            # Создаем горизонтальный layout для кнопок
            button_layout = QHBoxLayout()
            
            # Создаем кнопки
            self.addButton = QPushButton("Добавить")
            self.editButton = QPushButton("Редактировать")
            self.deleteButton = QPushButton("Удалить")
            self.completeButton = QPushButton("Выполнено")
            self.clearButton = QPushButton("Очистить список")
            
            # Добавляем кнопки в layout
            button_layout.addWidget(self.addButton)
            button_layout.addWidget(self.editButton)
            button_layout.addWidget(self.deleteButton)
            button_layout.addWidget(self.completeButton)
            button_layout.addWidget(self.clearButton)
            
            # Добавляем layout с кнопками в главный layout
            layout.addLayout(button_layout)
            
            # Настройка кнопок
            self.setup_buttons()
            
            logger.debug("Интерфейс настроен успешно")
        except Exception as e:
            logger.error(f"Ошибка при настройке интерфейса: {str(e)}")
            raise
    
    def setup_buttons(self):
        """Настройка кнопок интерфейса."""
        try:
            self.addButton.setIcon(QIcon("icons/add.png"))
            self.editButton.setIcon(QIcon("icons/edit.png"))
            self.deleteButton.setIcon(QIcon("icons/delete.png"))
            self.completeButton.setIcon(QIcon("icons/complete.png"))
            self.clearButton.setIcon(QIcon("icons/clear.png"))
            logger.debug("Кнопки настроены успешно")
        except Exception as e:
            logger.error(f"Ошибка при настройке кнопок: {str(e)}")
    
    def restore_table_state(self, state):
        """Восстановление состояния таблицы."""
        try:
            self.taskTable.setRowCount(len(state))
            for row, row_data in enumerate(state):
                for col, text in enumerate(row_data):
                    item = QTableWidgetItem(text)
                    if col != 3:  # Все колонки кроме приоритета не редактируемые
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.taskTable.setItem(row, col, item)
        except Exception as e:
            logger.error(f"Ошибка при восстановлении состояния таблицы: {str(e)}")
            logger.error(traceback.format_exc())
    
    def load_tasks(self, tasks):
        """Загрузка задач в таблицу."""
        try:
            # Блокируем сигналы таблицы
            self.taskTable.blockSignals(True)
            
            # Сохраняем текущую выделенную строку
            current_row = self.taskTable.currentRow()
            current_id = None
            if current_row >= 0:
                current_id = self.taskTable.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            
            self.taskTable.setRowCount(0)
            for task in tasks:
                row = self.taskTable.rowCount()
                self.taskTable.insertRow(row)
                
                # Заголовок
                title_item = QTableWidgetItem(task[1])
                title_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                title_item.setData(Qt.ItemDataRole.UserRole, task[0])  # Сохраняем ID в данных ячейки
                self.taskTable.setItem(row, 0, title_item)
                
                # Описание
                desc_item = QTableWidgetItem(task[2] or "")
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.taskTable.setItem(row, 1, desc_item)
                
                # Приоритет
                priority_item = QTableWidgetItem(str(task[3]))
                priority_item.setFlags(priority_item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.taskTable.setItem(row, 2, priority_item)
                
                # Статус
                status_item = QTableWidgetItem("Выполнено" if task[4] else "В работе")
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.taskTable.setItem(row, 3, status_item)
                
                # Если задача выполнена, меняем цвет фона
                if task[4]:
                    for col in range(self.taskTable.columnCount()):
                        item = self.taskTable.item(row, col)
                        if item:
                            item.setBackground(QColor("#e6ffe6"))
            
            # Восстанавливаем выделение
            if current_id:
                for row in range(self.taskTable.rowCount()):
                    if self.taskTable.item(row, 0).data(Qt.ItemDataRole.UserRole) == current_id:
                        self.taskTable.selectRow(row)
                        break
            
            self.taskTable.resizeColumnsToContents()
            logger.debug(f"Загружено {len(tasks)} задач")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке задач: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Разблокируем сигналы таблицы
            self.taskTable.blockSignals(False)
    
    def get_selected_task_ids(self):
        """Получение ID выбранных задач."""
        try:
            selected_rows = self.taskTable.selectionModel().selectedRows()
            return [self.taskTable.item(row.row(), 0).data(Qt.ItemDataRole.UserRole) for row in selected_rows]
        except Exception as e:
            logger.error(f"Ошибка при получении ID выбранных задач: {str(e)}")
            return []
    
    def get_selected_task_titles(self):
        """Получение заголовков выбранных задач."""
        try:
            selected_rows = self.taskTable.selectionModel().selectedRows()
            return [self.taskTable.item(row.row(), 0).text() for row in selected_rows]
        except Exception as e:
            logger.error(f"Ошибка при получении заголовков выбранных задач: {str(e)}")
            return []
    
    def get_current_task(self):
        """Получение текущей выбранной задачи."""
        try:
            selected = self.taskTable.currentRow()
            if selected < 0:
                return None
                
            task_id = self.taskTable.item(selected, 0).data(Qt.ItemDataRole.UserRole)
            title = self.taskTable.item(selected, 0).text()
            desc = self.taskTable.item(selected, 1).text()
            
            return {
                'id': task_id,
                'title': title,
                'description': desc
            }
        except Exception as e:
            logger.error(f"Ошибка при получении текущей задачи: {str(e)}")
            return None
    
    def load_styles(self):
        """Загрузка стилей приложения."""
        try:
            # Определяем системную тему
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            try:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                is_dark_theme = value == 0
            except FileNotFoundError:
                is_dark_theme = False
            finally:
                winreg.CloseKey(key)

            # Загружаем стили
            style_file = os.path.join(os.path.dirname(__file__), "styles.qss")
            with open(style_file, "r", encoding="utf-8") as f:
                styles = f.read()

            # Применяем стили
            self.parent.setStyleSheet(styles)
            
            # Устанавливаем темную тему для приложения
            if is_dark_theme:
                self.parent.setStyleSheet(self.parent.styleSheet() + """
                    QMainWindow {
                        background-color: #202020;
                    }
                    QTableWidget {
                        background-color: #202020;
                        color: #ffffff;
                    }
                    QLabel {
                        color: #ffffff;
                    }
                """)
            
            logger.debug("Стили загружены успешно")
        except Exception as e:
            logger.error(f"Ошибка при загрузке стилей: {str(e)}")
            raise
    
    def handle_drag_enter(self, event):
        """Обработка события входа в зону перетаскивания."""
        try:
            if event.source() == self.taskTable:
                event.acceptProposedAction()
            else:
                event.ignore()
        except Exception as e:
            logger.error(f"Ошибка при обработке dragEnterEvent: {str(e)}")
            event.ignore()
    
    def handle_drag_move(self, event):
        """Обработка события перемещения при перетаскивании."""
        try:
            if event.source() == self.taskTable:
                event.acceptProposedAction()
            else:
                event.ignore()
        except Exception as e:
            logger.error(f"Ошибка при обработке dragMoveEvent: {str(e)}")
            event.ignore()
    
    def handle_drop_event(self, event):
        """Обработка события отпускания при перетаскивании."""
        try:
            if event.source() != self.taskTable:
                event.ignore()
                return
            
            # Получаем индексы строк
            drop_row = self.taskTable.rowAt(int(event.position().y()))
            selected_rows = self.taskTable.selectionModel().selectedRows()
            
            if not selected_rows or drop_row < 0 or drop_row >= self.taskTable.rowCount():
                event.ignore()
                return
            
            source_row = selected_rows[0].row()
            
            # Если перетаскиваем на ту же строку, игнорируем событие
            if source_row == drop_row:
                event.ignore()
                return
            
            # Получаем ID перемещаемой задачи
            source_task_id = self.taskTable.item(source_row, 0).data(Qt.ItemDataRole.UserRole)
            
            # Получаем все задачи из базы данных
            tasks = self.parent.db_manager.get_all_tasks()
            
            # Находим индекс перемещаемой задачи в списке
            source_index = next(i for i, task in enumerate(tasks) if task[0] == source_task_id)
            
            # Перемещаем задачу в списке
            task = tasks.pop(source_index)
            tasks.insert(drop_row if drop_row < source_index else drop_row, task)
            
            # Обновляем порядок в базе данных
            self.parent.db_manager.reorder_tasks(tasks)
            
            # Перезагружаем задачи
            self.load_tasks(tasks)
            
            # Выделяем перемещенную строку
            self.taskTable.selectRow(drop_row)
            
            event.acceptProposedAction()
            
        except Exception as e:
            logger.error(f"Ошибка при обработке dropEvent: {str(e)}")
            logger.error(traceback.format_exc())
            # В случае ошибки перезагружаем задачи из базы данных
            tasks = self.parent.db_manager.get_all_tasks()
            self.load_tasks(tasks)
            event.ignore()
    
    def move_row_up(self, row):
        """Перемещение данных из указанной строки на одну позицию вверх."""
        # Сохраняем данные текущей строки
        current_data = []
        for col in range(self.taskTable.columnCount()):
            item = self.taskTable.item(row, col)
            if item:
                new_item = QTableWidgetItem(item.text())
                new_item.setFlags(item.flags())
                new_item.setBackground(item.background())
                if col == 0:
                    new_item.setData(Qt.ItemDataRole.UserRole, item.data(Qt.ItemDataRole.UserRole))
                current_data.append(new_item)
            else:
                current_data.append(None)
        
        # Перемещаем данные из верхней строки вниз
        for col in range(self.taskTable.columnCount()):
            item = self.taskTable.item(row - 1, col)
            if item:
                new_item = QTableWidgetItem(item.text())
                new_item.setFlags(item.flags())
                new_item.setBackground(item.background())
                if col == 0:
                    new_item.setData(Qt.ItemDataRole.UserRole, item.data(Qt.ItemDataRole.UserRole))
                self.taskTable.setItem(row, col, new_item)
        
        # Вставляем сохраненные данные в верхнюю строку
        for col in range(self.taskTable.columnCount()):
            if current_data[col]:
                self.taskTable.setItem(row - 1, col, current_data[col])
    
    def move_row_down(self, row):
        """Перемещение данных из указанной строки на одну позицию вниз."""
        # Сохраняем данные текущей строки
        current_data = []
        for col in range(self.taskTable.columnCount()):
            item = self.taskTable.item(row, col)
            if item:
                new_item = QTableWidgetItem(item.text())
                new_item.setFlags(item.flags())
                new_item.setBackground(item.background())
                if col == 0:
                    new_item.setData(Qt.ItemDataRole.UserRole, item.data(Qt.ItemDataRole.UserRole))
                current_data.append(new_item)
            else:
                current_data.append(None)
        
        # Перемещаем данные из нижней строки вверх
        for col in range(self.taskTable.columnCount()):
            item = self.taskTable.item(row + 1, col)
            if item:
                new_item = QTableWidgetItem(item.text())
                new_item.setFlags(item.flags())
                new_item.setBackground(item.background())
                if col == 0:
                    new_item.setData(Qt.ItemDataRole.UserRole, item.data(Qt.ItemDataRole.UserRole))
                self.taskTable.setItem(row, col, new_item)
        
        # Вставляем сохраненные данные в нижнюю строку
        for col in range(self.taskTable.columnCount()):
            if current_data[col]:
                self.taskTable.setItem(row + 1, col, current_data[col]) 