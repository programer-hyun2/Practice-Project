from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout,QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("program1")
        widget = QWidget()
        h_layout = QHBoxLayout()
        self.button1 = QPushButton("button1")
        self.button2 = QPushButton("button2")

        h_layout.addWidget(self.button1)
        h_layout.addWidget(self.button2)
        widget.setLayout(h_layout)
        self.setCentralWidget(widget)

        self.show()




app = QApplication([])
window = MainWindow()

window.show()
app.exec_()