from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.button_is_checked = False
        self.setWindowTitle("toggle_button0")
        self.button = QPushButton("Push to On")
        self.button.setCheckable = True
        self.button.clicked.connect(self.button_is_clicked)
        self.setCentralWidget(self.button)
        self.show()
        self.setStyleSheet("""
                           background-color: None;
                        border-style: inset;
                           font: 14px;
                           """)

    def button_is_clicked(self):
        self.button_is_checked = not self.button_is_checked
        if self.button_is_checked:
            self.button.setText("Push to Off")
            self.setStyleSheet("""
    background-color: rgb(10,255,124);
    border-style: outset;
    border-width: 2px;
    border-radius: 10px;
    color: rgb(255,255,255);
    font: bold 14px;
    font-color: rgb(255,255,255);
    min-width: 10em;
    padding: 6px;""")
        else:
            self.button.setText("Push to On")
            self.setStyleSheet("""
    background-color: None;
    font: 14px;
    min-width: 10em;
        """)
            

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()