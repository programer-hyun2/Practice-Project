from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication([])

window = QWidget()
window.setWindowTitle("MyPyQt5App")

window.show()

app.exec_()
