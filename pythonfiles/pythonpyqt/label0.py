from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("program1")
        widget = QWidget()
        v_layout = QVBoxLayout()
        self.input = QLineEdit()
        self.label = QLabel()

        v_layout.addWidget(self.label)
        v_layout.addWidget(self.input)
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)
        self.input.textChanged.connect(self.label.setText)
        self.show()

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()