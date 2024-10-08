from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Slider")

        widget = QWidget()
        v_layout = QVBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setSingleStep(5)
        
        v_layout.addWidget(self.slider)
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.show()

    def slider_value_changed(self,value):
        print(value)
        



app = QApplication([])
window = MainWindow()

window.show()
app.exec_()