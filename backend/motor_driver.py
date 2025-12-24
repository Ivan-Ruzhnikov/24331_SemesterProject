import serial
import time
import serial.tools.list_ports

class MotorDriver:
    def __init__(self):
        self.ser = None
        
    @staticmethod
    def get_available_ports():
        """Возвращает список доступных COM-портов"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self, port_name):
        """Подключение к Arduino"""
        try:
            self.ser = serial.Serial(port_name, 9600, timeout=1)
            time.sleep(2)
            return True
        except serial.SerialException as e:
            print(f"Ошибка подключения: {e}")
            return False

    def disconnect(self):
        """Отключение от Arduino"""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def move_to(self, target_position_mm):
        """Отправляет команду движения к относительной позиции"""
        if self.ser and self.ser.is_open:
            command = f"{target_position_mm}"
            self.ser.write(command.encode('utf-8'))
