import sys
import serial
import time
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget
import numpy as np
import serial.tools.list_ports

# --------------------------------------------- COMMUNICATION -------------------------------------------------- #

def open_Serial():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        details = [port.description, port.hwid, port.name,  port.interface, port.manufacturer, port.pid, port.serial_number]
        if "Arduino" in details or "FIDI" in details:
            print(f"Arduino found at: {port.device}")
            connection = serial.Serial(port.device, 9600, timeout=1)
            return connection
    while(True):
        user_input = input("Manually enter Arduino COM: ")
        try:
            connection = serial.Serial(user_input, 9600, timeout=1)
            return connection  # Return connection if successful
        except serial.SerialException as e:
            print(f"Error opening {user_input}: {e}. Please try again.")
        

def send_serial_data(ser, message):
    if ser and ser.is_open:         # Ensure serial port is open
        ser.write(message.encode()) # encode() turns the message into bit-stream
        ser.flush()                 # forces the program to wait until everything in the output buffer are send
        
        time.sleep(0.05)
        received = read_serial_data(ser)
        if received != "ACK":
            print(received)
            send_serial_data(ser,message)
        print(received)
    else:
        print("Error: Serial port not open!")


def read_serial_data(ser):
    if ser and ser.is_open and ser.in_waiting > 0:  # Check if data is available
        received_data = ser.readline()              # Read data until '\n'

        if received_data:
            received_data = received_data.decode(errors="replace").strip()
            return received_data
    return None
            


# ---------------------------------------- PAINT_APP -------------------------------------------------- #

class PaintApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painter App")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # Lists to store coordinates
        self.x_coords = []
        self.y_coords = []

        # Try to Open Serial Connection
        self.ser = None
        try:
            self.ser = open_Serial()
            self.ser = serial.Serial(find_Serial(), 9600, timeout=1)
        except serial.SerialException as e:
            print(f"Error: {e}")
            self.ser = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.x_coords.append(event.x())
            self.y_coords.append(self.height() - event.y())
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))

        # Draw trajectory
        if len(self.x_coords) > 1:
            for i in range(1, len(self.x_coords)):
                painter.drawLine(QPoint(self.x_coords[i-1], self.height() - self.y_coords[i-1]),
                                 QPoint(self.x_coords[i], self.height() - self.y_coords[i]))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.x_coords = []  # Clear downsampled coordinates
            self.y_coords = []
            self.update()

        elif event.key() == Qt.Key_S:  # Save points when 'S' is pressed
            self.send_coords()


    def send_coords(self):
        """Sends the downsampled coordinates via serial."""
        x_send = list(np.round(np.array(self.x_coords)*10/800, 2))
        y_send = list(np.round(np.array(self.y_coords)*6/600 + 10, 2))

        #------- save to .txt --------#
        with open("trajectory_points.txt", "w") as file:
                for x, y in zip(x_send, y_send):
                    file.write(f"{x},{y}\n")
        #-----------------------------#
        
        for x, y in zip(x_send, y_send):
            message = f"{x},{y}\n"  # Format: "12.34,56.78\n"
            send_serial_data(self.ser, message)
            time.sleep(0.1)  # Short delay for stability

        send_serial_data(self.ser, "stop\n")
        

# ------------------------------------- MAIN ------------------------------------------ #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    
    sys.exit(app.exec_())
