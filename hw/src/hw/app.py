import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello World")
        self.setMinimumSize(400, 200)
        
        # Create a central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create a layout
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create a label with Hello World text
        label = QtWidgets.QLabel("Hello World!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(label)


class App:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow()

    def main_loop(self):
        self.window.show()
        return self.app.exec()


def main():
    return App().main_loop()