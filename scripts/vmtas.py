import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel, QFileDialog, \
    QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QSplitter, QCheckBox

import json
import shutil
import uuid
from pathlib import Path


window_titles = [
    "VMTAS",
    "VMTAS File Addition",
    "VMTAS Login"
]

RUN_STORAGE_DIR = Path("../data")
RUN_STORAGE_DIR.mkdir(exist_ok=True)
RUN_REGISTRY_FILE = RUN_STORAGE_DIR / "runs.json"

run_1_file = None
run_2_file = None




def load_runs():
    if RUN_REGISTRY_FILE.exists():
        try:
            with open(RUN_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_runs(runs_dict):
    with open(RUN_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(runs_dict, f, indent=4)


class MainWindow(QMainWindow):
    combobox_file_1 = None
    combobox_file_2 = None
    combobox_delete_file = None
    splitter_options = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle(window_titles[0])
        self.setFixedSize(QSize(1200, 800))
        self.setMinimumSize(QSize(1000, 600))
        self.setWindowIcon(QIcon("../img/vmtas_icon.ico"))
        self.splitter_options = QSplitter(Qt.Orientation.Vertical)
        self.splitter_options.setHandleWidth(2)
        self.splitter_options.setStyleSheet("""
            QSplitter::handle:vertical {
                background-color: #6B6B6B;
                image: none;
            }
            QSplitter::handle:vertical:hover {
                background-color: #94A3B8;
            }
            /* Visual indicator lines inside the handle */
            QSplitter::handle:vertical:pressed {
                background-color: #64748B;
            }
        """)
        self.setCentralWidget(self.splitter_options)

        self._build_file_ui()
        self._build_options_ui()

    def _build_file_ui(self):
        layout_file_selection = QVBoxLayout()
        layout_file_selection.setContentsMargins(24, 24, 24, 24)
        layout_file_selection.setSpacing(10)

        button_add_file = QPushButton("Add Run .csv")
        button_add_file.clicked.connect(self.button_add_file_on_click)

        button_refresh_runs = QPushButton("Refresh Available Runs")
        button_refresh_runs.clicked.connect(self.refresh_runs)

        label_pick_file_1 = QLabel("Select First Run")
        self.combobox_file_1 = QComboBox()
        self.populate_run_dropdown(self.combobox_file_1)

        layout_buttons_file_1 = QHBoxLayout()
        button_confirm_file_1 = QPushButton("Confirm")
        button_confirm_file_1.clicked.connect(
            lambda: self.select_file_1(self.combobox_file_1)
        )
        button_clear_file_1 = QPushButton("Clear")
        button_clear_file_1.clicked.connect(self.clear_file_1)
        layout_buttons_file_1.addWidget(button_confirm_file_1)
        layout_buttons_file_1.addWidget(button_clear_file_1)

        label_pick_file_2 = QLabel("Select Second Run")
        self.combobox_file_2 = QComboBox()
        self.populate_run_dropdown(self.combobox_file_2)

        layout_buttons_file_2 = QHBoxLayout()
        button_confirm_file_2 = QPushButton("Confirm")
        button_confirm_file_2.clicked.connect(
            lambda: self.select_file_2(self.combobox_file_2)
        )
        button_clear_file_2 = QPushButton("Clear")
        button_clear_file_2.clicked.connect(self.clear_file_2)
        layout_buttons_file_2.addWidget(button_confirm_file_2)
        layout_buttons_file_2.addWidget(button_clear_file_2)

        label_delete_file = QLabel("Delete Run")
        self.combobox_delete_file = QComboBox()
        self.populate_run_dropdown(self.combobox_delete_file)
        button_confirm_delete_file = QPushButton("Confirm")
        button_confirm_delete_file.clicked.connect(
            lambda: self.button_delete_run(self.combobox_delete_file)
        )

        layout_file_selection.addWidget(button_add_file)
        layout_file_selection.addWidget(button_refresh_runs)
        layout_file_selection.addWidget(label_pick_file_1)
        layout_file_selection.addWidget(self.combobox_file_1)
        layout_file_selection.addLayout(layout_buttons_file_1)
        layout_file_selection.addWidget(label_pick_file_2)
        layout_file_selection.addWidget(self.combobox_file_2)
        layout_file_selection.addLayout(layout_buttons_file_2)
        layout_file_selection.addWidget(label_delete_file)
        layout_file_selection.addWidget(self.combobox_delete_file)
        layout_file_selection.addWidget(button_confirm_delete_file)
        layout_file_selection.addStretch()

        widget = QWidget()
        widget.setLayout(layout_file_selection)
        self.splitter_options.addWidget(widget)

    def _build_options_ui(self):
        layout_option_selection = QVBoxLayout()
        layout_option_selection.setContentsMargins(24, 24, 24, 24)
        layout_option_selection.setSpacing(10)

        # TODO: Add remaining datapoints and separate into two columns for space purposes.
        label_select_options = QLabel("Select Visible Datapoints")
        checkbox_track_map = QCheckBox("Track Map")
        checkbox_file_1_heatmap = QCheckBox("Run 1 Speed Heatmap")
        checkbox_file_2_heatmap = QCheckBox("Run 2 Speed Heatmap")
        button_confirm = QPushButton("Confirm")

        layout_option_selection.addWidget(label_select_options)
        layout_option_selection.addWidget(checkbox_track_map)
        layout_option_selection.addWidget(checkbox_file_1_heatmap)
        layout_option_selection.addWidget(checkbox_file_2_heatmap)

        layout_option_selection.addWidget(button_confirm)
        layout_option_selection.addStretch()

        widget = QWidget()
        widget.setLayout(layout_option_selection)
        self.splitter_options.addWidget(widget)

    @staticmethod
    def populate_run_dropdown(combo_box: QComboBox):
        combo_box.clear()
        runs = load_runs()

        for run_name, details in runs.items():
            combo_box.addItem(run_name, userData=details["stored_path"])

    def refresh_runs(self):
        self.populate_run_dropdown(self.combobox_file_1)
        self.populate_run_dropdown(self.combobox_file_2)
        self.populate_run_dropdown(self.combobox_delete_file)


    @staticmethod
    def select_file_1(combo_box: QComboBox):
        global run_1_file
        selected_csv_path = combo_box.currentData()
        run_1_file = selected_csv_path
        print(run_1_file)

    @staticmethod
    def select_file_2(combo_box: QComboBox):
        global run_2_file
        selected_csv_path = combo_box.currentData()
        run_2_file = selected_csv_path
        print(run_2_file)

    @staticmethod
    def clear_file_1():
        global run_1_file
        run_1_file = None

    @staticmethod
    def clear_file_2():
        global run_2_file
        run_2_file = None

    @staticmethod
    def button_add_file_on_click():
        window_file_selection.show()

    def button_delete_run(self, combo_box: QComboBox):
        selected_name = combo_box.currentText().strip()

        if not selected_name:
            QMessageBox.warning(self, "No Selection", "Please select a run to delete")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure want to permanently delete run '{selected_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        runs = load_runs()

        if selected_name not in runs:
            QMessageBox.warning(
                self, "Not Found", f"Run '{selected_name}' does not exist in the registry."
            )
            return

        file_info = runs[selected_name]
        stored_path_str = file_info.get("stored_path", "")
        if stored_path_str:
            file_path = Path(stored_path_str)
            if file_path.exists():
                try:
                    file_path.unlink()
                except OSError as e:
                    QMessageBox.critical(
                        self, "File Error", f"Failed to delete CSV file: {e}"
                    )
                    return
        del runs[selected_name]
        save_runs(runs)

        current_index = combo_box.currentIndex()
        self.combobox_file_1.removeItem(current_index)
        self.combobox_file_2.removeItem(current_index)
        self.combobox_delete_file.removeItem(current_index)

        QMessageBox.information(
            self, "Success", f"Run '{selected_name}' has been deleted."
        )




class FileAdditionWindow(QWidget):
    file_to_add = None
    label_current_selected = None
    textbox_name = None

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
        self.textbox_name = QLineEdit()
        self.label_current_selected = QLabel("Current File Selected: ")
        button_file = QPushButton("Select Run File .csv")
        button_file.clicked.connect(self.button_select_file_on_click)
        button_confirm = QPushButton("Confirm")
        button_confirm.clicked.connect(self.button_confirm_on_click)

        layout.addWidget(label_name)
        layout.addWidget(self.textbox_name)
        layout.addWidget(self.label_current_selected)
        layout.addWidget(button_file)
        layout.addWidget(button_confirm)
        self.setLayout(layout)

    def button_select_file_on_click(self):
        self.file_to_add = QFileDialog.getOpenFileName(self, self.tr("Select File"), "", self.tr("CSV Files (*.csv)"))
        if self.file_to_add[0]:
            self.label_current_selected.setText("Current File Selected: " + self.file_to_add[0].rpartition('/')[-1])
        else:
            self.label_current_selected.setText("Current File Selected: ")

    def button_confirm_on_click(self):
        run_file = self.file_to_add[0] if self.file_to_add else None
        run_name = self.textbox_name.text().strip()

        if not run_file and not run_name:
            QMessageBox.critical(self, "Error", "Must provide a name and file for the saved run!", QMessageBox.StandardButton.Ok)
            return
        elif not run_file:
            QMessageBox.critical(self, "Error", "Must provide a file for the saved run!", QMessageBox.StandardButton.Ok)
            return
        elif not run_name:
            QMessageBox.critical(self, "Error", "Must provide a name for the saved run!", QMessageBox.StandardButton.Ok)
            return

        runs = load_runs()
        if run_name in runs:
            QMessageBox.warning(self, "Duplicate Run Name",f"A run named '{run_name}' already exists. Choose a different name.")
            return

        unique_filename = f"{uuid.uuid4().hex}.csv"
        destination_path = RUN_STORAGE_DIR / unique_filename

        try:
            shutil.copy2(run_file, destination_path)

            runs[run_name] = {
                "stored_path": str(destination_path.resolve()),
                "original_filename": Path(run_file).name
            }
            save_runs(runs)

            QMessageBox.information(self, "Success", f"Run '{run_name}' saved successfully.")
            self.textbox_name.clear()
            self.file_to_add = None
            self.label_current_selected.setText("Current File Selected: ")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save file: {str(e)}")



app = QApplication(sys.argv)

window = MainWindow()
window_file_selection = FileAdditionWindow()

window.show()

app.exec()