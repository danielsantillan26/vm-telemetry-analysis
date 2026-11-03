import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel, QFileDialog, \
    QComboBox, QLineEdit

window_titles = [
    "VMTAS",
    "VMTAS File Select",
    "VMTAS Login"
]



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(window_titles[0])
        self.setFixedSize(QSize(1200, 800))
        self.setMinimumSize(QSize(1000, 600))
        self.setWindowIcon(QIcon("../img/vmtas_icon.ico"))
        self._build_ui()

    def _build_ui(self):
        layout_file_selection = QVBoxLayout()
        button_add_file = QPushButton("Add Run .csv")
        button_add_file.clicked.connect(self.button_add_file_on_click)

        label_pick_file_1 = QLabel("Select First Run")
        combobox_file_1 = QComboBox()
        button_confirm_file_1 = QPushButton("Confirm")

        label_pick_file_2 = QLabel("Select Second Run")
        combobox_file_2 = QComboBox()
        button_confirm_file_2 = QPushButton("Confirm")

        label_delete_file = QLabel("Delete Run")
        combobox_delete_file = QComboBox()
        button_confirm_delete_file = QPushButton("Confirm")

        layout_file_selection.addWidget(button_add_file)
        layout_file_selection.addWidget(label_pick_file_1)
        layout_file_selection.addWidget(combobox_file_1)
        layout_file_selection.addWidget(button_confirm_file_1)
        layout_file_selection.addWidget(label_pick_file_2)
        layout_file_selection.addWidget(combobox_file_2)
        layout_file_selection.addWidget(button_confirm_file_2)
        layout_file_selection.addWidget(label_delete_file)
        layout_file_selection.addWidget(combobox_delete_file)
        layout_file_selection.addWidget(button_confirm_delete_file)

        widget = QWidget()
        widget.setLayout(layout_file_selection)

        self.setCentralWidget(widget)

    def button_add_file_on_click(self):
        window = FileAdditionWindow()
        window.show()
        # file_to_add = QFileDialog.getOpenFileName(self, self.tr("Select File"), "", self.tr("CSV Files (*.csv)"))




class FileAdditionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(window_titles[1])
        self.setFixedSize(QSize(500, 500))
        self.setMinimumSize(QSize(500, 500))
        self.setMaximumSize(QSize(500, 500))
        self.setWindowIcon(QIcon("../img/vmtas_icon.ico"))
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        label_name = QLabel("Enter Run Name:")
        textbox_name = QLineEdit()

        widget = QWidget()
        widget.setLayout(layout)



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()