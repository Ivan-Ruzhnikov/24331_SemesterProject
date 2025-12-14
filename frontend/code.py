import sys
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QDoubleSpinBox, QRadioButton,
    QButtonGroup, QLabel, QComboBox, QMenu,
    QMessageBox
)
from PyQt6.QtGui import QDesktopServices, QAction
from PyQt6.QtCore import QSize, Qt, QUrl



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Adjustment sensor")
        self.setFixedSize(QSize(700, 400))

        # Текущее положение датчика
        self.current_position = 0.0
        self.zero_position = 0.0


        self.readme = os.path.join(os.path.dirname(os.path.abspath(__file__)),"README.txt")

        # --- Верхняя панель: выбор датчика и индикация позиции ---
        top_layout = QHBoxLayout()

        sensor_label = QLabel("Датчик:")
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItems(["____"])

        self.position_label = QLabel("Позиция: 0.000 cм")

        top_layout.addWidget(sensor_label)
        top_layout.addWidget(self.sensor_combo)
        top_layout.addStretch()
        top_layout.addWidget(self.position_label)

        # --- Центральная часть: расстояние + направление ---
        center_layout = QGridLayout()

        distance_label = QLabel("Расстояние, cм:")
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setDecimals(3)
        self.distance_spin.setSingleStep(0.1)
        self.distance_spin.setValue(10.0)

        center_layout.addWidget(distance_label, 0, 0)
        center_layout.addWidget(self.distance_spin, 0, 1)

        # Кнопки направления
        direction_label = QLabel("Направление:")
        self.forward_radio = QRadioButton("Вперед")
        self.backward_radio = QRadioButton("Назад")

        self.direction_group = QButtonGroup(self)
        self.direction_group.addButton(self.forward_radio)
        self.direction_group.addButton(self.backward_radio)
        self.forward_radio.setChecked(True)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.forward_radio)
        dir_layout.addWidget(self.backward_radio)

        center_layout.addWidget(direction_label, 1, 0)
        center_layout.addLayout(dir_layout, 1, 1)

        # Быстрые кнопки расстояния
        quick_label = QLabel("Быстрые расстояния:")
        quick_layout = QHBoxLayout()
        quick_distances = [1.0, 5.0, 10.0, 20.0]

        for d in quick_distances:
            btn = QPushButton(f"{d} мм")
            btn.clicked.connect(lambda _, value=d: self.set_quick_distance(value))
            quick_layout.addWidget(btn)

        center_layout.addWidget(quick_label, 2, 0)
        center_layout.addLayout(quick_layout, 2, 1)

        # Кнопки управления
        bottom_layout = QHBoxLayout()

        self.set_zero_btn = QPushButton("Установить ноль")
        self.set_zero_btn.clicked.connect(self.set_zero)

        self.move_btn = QPushButton("Двигать")
        self.move_btn.clicked.connect(self.move_sensor)

        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.clicked.connect(self.emergency_stop)

        bottom_layout.addWidget(self.set_zero_btn)
        bottom_layout.addWidget(self.move_btn)
        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addStretch()

        # --- Общий layout ---
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # ========== ЛОГИКА ==========

    def set_quick_distance(self, value: float):
        """Установить расстояние из быстрой кнопки."""
        self.distance_spin.setValue(value)

    def set_zero(self):
        """Установить текущую позицию как ноль."""
        self.zero_position = self.current_position
        self.update_position_label()

    def move_sensor(self):
        """Пример логики перемещения датчика.
        Сюда нужно подставить реальные вызовы к твоему контроллеру."""
        distance = self.distance_spin.value()

        # Учёт направления
        if self.backward_radio.isChecked():
            distance = -abs(distance)
        else:
            distance = abs(distance)

        # TODO: вызвать функцию управления датчиком, передать distance
        # например: sensor.move(distance)

        # Для примера просто обновляем виртуальную позицию
        self.current_position += distance
        self.update_position_label()

    def emergency_stop(self):
        """Аварийная остановка датчика.
        Здесь должен быть код, который реально останавливает движение."""
        # TODO: вызвать функцию аварийной остановки контроллера
        print("EMERGENCY STOP!")

    def update_position_label(self):
        """Обновление текста текущей позиции с учетом нуля."""
        relative_pos = self.current_position - self.zero_position
        self.position_label.setText(f"Позиция: {relative_pos:.3f} мм")

    # ========== КОНТЕКСТНОЕ МЕНЮ (ReadMe) ==========

    def contextMenuEvent(self, event):
        """Вызывается при правом клике по окну."""
        context = QMenu(self)

        readme_action = QAction("ReadMe", self)
        readme_action.triggered.connect(self.open_readme)

        context.addAction(readme_action)
        context.exec(event.globalPos())

    def open_readme(self):
        """Открыть файл инструкции."""
        if not os.path.exists(self.readme):
            QMessageBox.warning(self, "ReadMe", "Файл инструкции не найден.")
            return

        url = QUrl.fromLocalFile(self.readme)
        ok = QDesktopServices.openUrl(url)
        if not ok:
            QMessageBox.warning(self, "ReadMe", "Не удалось открыть файл инструкции.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
