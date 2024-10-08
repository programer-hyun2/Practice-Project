from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDial, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Slider")
        
        widget = QWidget()
        v_layout = QVBoxLayout()

        self.slider = QDial()
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setSingleStep(5)

        self.label = QLabel("0")

        v_layout.addWidget(self.slider)
        v_layout.addWidget(self.label)
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.show()

    def slider_value_changed(self,value):
        self.label.setText(str(value))

app = QApplication([])
window = MainWindow()

window.show()
app.exec_()