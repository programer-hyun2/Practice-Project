from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("button0")
        button = QPushButton("PUSH")
        button.setCheckable = True
        button.clicked.connect(self.button_is_clicked)
        self.setCentralWidget(button)
        self.show()

    def button_is_clicked(self):
        print("Clicked!!")

app = QApplication([])
window = MainWindow()

window.show()
app.exec_()