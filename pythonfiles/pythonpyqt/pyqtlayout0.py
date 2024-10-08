from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    valueR,valueG,valueB = 0,0,0
    def __init__(self):
        super().__init__()
        self.setWindowTitle("program1")
        widget = QWidget()
        h_layout = QHBoxLayout()
        v1_layout = QVBoxLayout()
        v2_layout = QVBoxLayout()
        self.button1 = QPushButton("0")
        self.button1.setStyleSheet("background-color: white")
        self.button2 = QPushButton("0")
        self.button2.setStyleSheet("background-color: white")
        self.button3 = QPushButton("0")
        self.button3.setStyleSheet("background-color: white")
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setMinimum(0)
        self.slider1.setMaximum(255)
        self.slider1.setSingleStep(5)
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(255)
        self.slider2.setSingleStep(5)
        self.slider3 = QSlider(Qt.Horizontal)
        self.slider3.setMinimum(0)
        self.slider3.setMaximum(255)
        self.slider3.setSingleStep(5)
        
        v1_layout.addWidget(self.button1)
        v1_layout.addWidget(self.button2)
        v1_layout.addWidget(self.button3)

        v2_layout.addWidget(self.slider1)
        v2_layout.addWidget(self.slider2)
        v2_layout.addWidget(self.slider3)

        h_layout.addLayout(v1_layout)
        h_layout.addLayout(v2_layout)
        widget.setLayout(h_layout)
        
        self.setCentralWidget(widget)
        
        self.show()

        self.slider1.valueChanged.connect(self.slider1_value_changed)
        self.slider2.valueChanged.connect(self.slider2_value_changed)
        self.slider3.valueChanged.connect(self.slider3_value_changed)
        self.button1.clicked.connect(self.button1_clicked)
        self.button2.clicked.connect(self.button2_clicked)    
        self.button3.clicked.connect(self.button3_clicked)
    
    def slider1_value_changed(self,value):
        self.button1.setText(str(value))
        self.valueR = value
        self.setStyleSheet("background-color: rgb({},{},{})".format(self.valueR,self.valueG,self.valueB))
    def slider2_value_changed(self,value):
        self.button2.setText(str(value))
        self.valueG = value
        self.setStyleSheet("background-color: rgb({},{},{})".format(self.valueR,self.valueG,self.valueB))
    def slider3_value_changed(self,value):
        self.button3.setText(str(value))
        self.valueB = value
        self.setStyleSheet("background-color: rgb({},{},{})".format(self.valueR,self.valueG,self.valueB))

    def button1_clicked(self):
        self.slider1.setValue(0)
    def button2_clicked(self):
        self.slider2.setValue(0)
    def button3_clicked(self):
        self.slider3.setValue(0)

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()