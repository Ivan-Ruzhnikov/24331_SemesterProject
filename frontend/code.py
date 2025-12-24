import sys
import os
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QDoubleSpinBox, QRadioButton,
    QButtonGroup, QLabel, QComboBox, QMenu,
    QMessageBox, QTextEdit, QGroupBox
)
from PyQt6.QtGui import QDesktopServices, QAction
from PyQt6.QtCore import QSize, QUrl, Qt
from backend.motor_driver import MotorDriver


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.setFixedSize(QSize(950, 450))
        self.driver = MotorDriver()
        self.readme = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.txt")
        self.init_ui()
        self.log_message("Программа запущена. Режим: Относительное перемещение.")

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Верхняя панель (Подключение)
        top_layout = QHBoxLayout()
        sensor_label = QLabel("Порт:")
        self.sensor_combo = QComboBox()
        self.refresh_ports()

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.refresh_ports)

        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.setCheckable(True)
        self.connect_btn.clicked.connect(self.toggle_connection)

        top_layout.addWidget(sensor_label)
        top_layout.addWidget(self.sensor_combo)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.connect_btn)
        top_layout.addStretch()

        # Центральная панель (Движение)
        center_layout = QGridLayout()

        distance_label = QLabel("Смещение, мм:")
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setDecimals(3)
        self.distance_spin.setRange(0, 1000)
        self.distance_spin.setSingleStep(1.0)
        self.distance_spin.setValue(10.0)

        center_layout.addWidget(distance_label, 0, 0)
        center_layout.addWidget(self.distance_spin, 0, 1)

        # Направление
        direction_label = QLabel("Направление:")
        self.forward_radio = QRadioButton("Вперед (+)")
        self.backward_radio = QRadioButton("Назад (-)")
        self.direction_group = QButtonGroup(self)
        self.direction_group.addButton(self.forward_radio)
        self.direction_group.addButton(self.backward_radio)
        self.forward_radio.setChecked(True)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.forward_radio)
        dir_layout.addWidget(self.backward_radio)

        center_layout.addWidget(direction_label, 1, 0)
        center_layout.addLayout(dir_layout, 1, 1)

        # Быстрые кнопки
        quick_label = QLabel("Быстрый выбор:")
        quick_layout = QHBoxLayout()
        quick_distances = [1.0, 5.0, 10.0, 20.0, 50.0]
        for d in quick_distances:
            btn = QPushButton(f"{d} мм")
            btn.clicked.connect(lambda _, value=d: self.set_quick_distance(value))
            quick_layout.addWidget(btn)

        center_layout.addWidget(quick_label, 2, 0)
        center_layout.addLayout(quick_layout, 2, 1)

        # Нижняя панель (Действия)
        bottom_layout = QHBoxLayout()

        self.move_btn = QPushButton("ДВИГАТЬ")
        self.move_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 14px;")
        self.move_btn.setMinimumHeight(45)
        self.move_btn.clicked.connect(self.move_sensor)

        # Кнопка ТЕСТ - ДЛЯ СДАЧИ ПРОЕКТА. Нужно потом убрать!!!
        self.test_btn = QPushButton("ТЕСТ")
        self.test_btn.setCheckable(True)
        self.test_btn.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")
        self.test_btn.setMinimumHeight(45)
        self.test_btn.clicked.connect(self.toggle_test_mode)

        bottom_layout.addWidget(self.move_btn)
        bottom_layout.addWidget(self.test_btn)

        left_layout.addLayout(top_layout)
        left_layout.addSpacing(20)
        left_layout.addLayout(center_layout)
        left_layout.addStretch()
        left_layout.addLayout(bottom_layout)
        left_panel.setLayout(left_layout)

        # Журнал операций
        right_group = QGroupBox("Журнал операций")
        right_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        right_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: Consolas; font-size: 11px;")

        clear_btn = QPushButton("Очистить")
        clear_btn.clicked.connect(self.clear_log)

        right_layout.addWidget(self.log_text)
        right_layout.addWidget(clear_btn)
        right_group.setLayout(right_layout)

        # Добавляем панели в главное окно
        # Левая часть занимает 60% ширины, правая 40%
        main_layout.addWidget(left_panel, 6)
        main_layout.addWidget(right_group, 4)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Блокируем кнопки до подключения
        self.enable_controls(False)

    # ЛОГИКА

    def log_message(self, message):
        # Пишет лог в окно и в файл - Запись в файл потом убрать!!!
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        full_msg = f"{timestamp} {message}"

        # В окно
        self.log_text.append(full_msg)

        # Автопрокрутка вниз
        self.log_text.moveCursor(self.log_text.textCursor().MoveOperation.End)

    def clear_log(self):
        self.log_text.clear()

    def refresh_ports(self):
        self.sensor_combo.clear()
        ports = self.driver.get_available_ports()
        if ports:
            self.sensor_combo.addItems(ports)
        else:
            self.sensor_combo.addItem("Нет устройств")

    def toggle_connection(self):
        if self.connect_btn.isChecked():
            port = self.sensor_combo.currentText()
            if port == "Нет устройств":
                self.connect_btn.setChecked(False)
                return

            self.log_message(f"Подключение к {port}...")
            if self.driver.connect(port):
                self.connect_btn.setText("Отключить")
                self.enable_controls(True)
                self.log_message("Успешно подключено.")
                QMessageBox.information(self, "Успех", f"Порт {port} открыт.")
            else:
                self.connect_btn.setChecked(False)
                self.log_message("Ошибка подключения.")
                QMessageBox.critical(self, "Ошибка", "Не удалось открыть порт")
        else:
            self.driver.disconnect()
            self.connect_btn.setText("Подключить")
            self.enable_controls(False)
            self.log_message("Отключено.")

    def enable_controls(self, enable):
        self.move_btn.setEnabled(enable)
        self.test_btn.setEnabled(True)

    def set_quick_distance(self, value: float):
        self.distance_spin.setValue(value)

    def move_sensor(self):
        # Отправка команды движения
        distance = self.distance_spin.value()

        # Определяем знак направления
        if self.backward_radio.isChecked():
            distance = -abs(distance)
        else:
            distance = abs(distance)

        self.log_message(f"Команда: Сдвиг на {distance} мм")

        try:
            self.driver.move_to(distance)
            self.log_message("Команда отправлена.")

        except AttributeError:
            QMessageBox.critical(self, "Ошибка", "Ошибка драйвера: метод move_to не найден.")
        except Exception as e:
            self.log_message(f"Сбой при отправке: {e}")

    def toggle_test_mode(self): # Для сдачи проекта - потом убрать!!!
        # Режим ТЕСТ
        is_test = self.test_btn.isChecked()
        if is_test:
            # ПОПЫТКА ВКЛЮЧИТЬ ТЕСТ
            # Если мы уже подключены к реальному Arduino — запрещаем тест
            if self.connect_btn.isChecked():
                QMessageBox.warning(self, "Конфликт", "Сначала отключитесь от реального порта!")
                self.test_btn.setChecked(False)  # Отжимаем кнопку обратно
                return

            # Включаем интерфейс
            self.enable_controls(True)
            # Блокируем кнопку подключения
            self.connect_btn.setEnabled(False)
            self.test_btn.setText("Выкл. ТЕСТ")
            self.log_message("Режим ТЕСТ включен (симуляция).")

        else:
            # ВЫКЛЮЧЕНИЕ ТЕСТА
            self.enable_controls(False)
            # Возвращаем возможность подключаться
            self.connect_btn.setEnabled(True)
            self.test_btn.setText("ТЕСТ")
            self.log_message("Режим ТЕСТ выключен.")

    def contextMenuEvent(self, event):
        context = QMenu(self)
        readme_action = QAction("ReadMe", self)
        readme_action.triggered.connect(self.open_readme)
        context.addAction(readme_action)
        context.exec(event.globalPos())

    def open_readme(self):
        if not os.path.exists(self.readme):
            QMessageBox.warning(self, "ReadMe", "Файл инструкции не найден.")
            return
        url = QUrl.fromLocalFile(self.readme)
        QDesktopServices.openUrl(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
