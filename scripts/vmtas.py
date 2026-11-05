import math
import sys
import time

import numpy as np
import pandas as pd
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel, QFileDialog, \
    QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QSplitter, QCheckBox, QSlider

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
    splitter_options: QSplitter
    splitter_data: QSplitter
    splitter_main: QSplitter
    window_file: FileWindow
    window_options: OptionsWindow
    window_data: DataWindow
    active_run_1: pd.DataFrame | None
    active_run_2: pd.DataFrame | None

    def __init__(self):
        super().__init__()
        self.setWindowTitle(window_titles[0])
        self.resize(QSize(1200, 800))
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
            QSplitter::handle:vertical:pressed {
                background-color: #64748B;
            }
        """)
        self.splitter_options.resize(300, 800)
        self.splitter_options.setMinimumSize(300, 600)
        self.splitter_options.setMaximumWidth(500)

        self.splitter_data = QSplitter(Qt.Orientation.Vertical)
        self.splitter_data.setHandleWidth(2)
        self.splitter_data.setStyleSheet("""
            QSplitter::handle:vertical {
                background-color: #6B6B6B;
                image: none;
            }
            QSplitter::handle:vertical:hover {
                background-color: #94A3B8;
            }
            QSplitter::handle:vertical:pressed {
                background-color: #64748B;
            }
        """)
        self.splitter_data.resize(900, 800)
        self.splitter_data.setMinimumSize(750, 600)

        self.splitter_main = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_main.setHandleWidth(2)
        self.splitter_main.setStyleSheet("""
            QSplitter::handle:horizontal {
                background-color: #6B6B6B;
                image: none;
            }
            QSplitter::handle:horizontal:hover {
                background-color: #94A3B8;
            }
            QSplitter::handle:horizontal:pressed {
                background-color: #64748B;
            }
        """)

        self.window_file = FileWindow()
        self.splitter_options.addWidget(self.window_file)
        self.window_options = OptionsWindow()
        self.splitter_options.addWidget(self.window_options)
        self.window_data = DataWindow()
        self.splitter_data.addWidget(self.window_data)
        self._build_stats_ui()

        self.splitter_main.addWidget(self.splitter_options)
        self.splitter_main.addWidget(self.splitter_data)
        self.setCentralWidget(self.splitter_main)

        self.active_run_1 = None
        self.active_run_2 = None

        self.window_file.run_1_updated.connect(self.handle_run_1_update)
        self.window_file.run_2_updated.connect(self.handle_run_2_update)

    def _build_stats_ui(self):
        self.splitter_data.addWidget(QWidget())

    def handle_run_1_update(self, df: pd.DataFrame | None):
        self.active_run_1 = df
        self.rework_slider()

    def handle_run_2_update(self, df: pd.DataFrame | None):
        self.active_run_2 = df
        self.rework_slider()

    def rework_slider(self):
        candidates = []

        for df in (self.active_run_1, self.active_run_2):
            if df is not None and not df.empty and df.shape[1] >= 3:
                series = pd.to_numeric(df.iloc[:, 2], errors="coerce").dropna()
                if not series.empty:
                    val = series.max()
                    if not np.isnan(val):
                        candidates.append(val)

        if candidates:
            overall_max = int(math.ceil(max(candidates)))
            self.window_data.update_slider_max(overall_max)
        else:
            self.window_data.update_slider_max(0)


class FileWindow(QWidget):
    run_1_updated = pyqtSignal(object)
    run_2_updated = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 300)
        self._build_ui()

    def _build_ui(self):
        layout_file_selection = QVBoxLayout()
        layout_file_selection.setContentsMargins(24, 24, 24, 24)
        layout_file_selection.setSpacing(10)

        button_add_file = QPushButton("Add Run .csv")
        button_add_file.clicked.connect(self.button_add_file_on_click)

        button_refresh_runs = QPushButton("Refresh Available Runs")
        button_refresh_runs.clicked.connect(self.refresh_runs)

        self.label_pick_file_1 = QLabel("Select First Run")
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

        self.label_pick_file_2 = QLabel("Select Second Run")
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
        layout_file_selection.addWidget(self.label_pick_file_1)
        layout_file_selection.addWidget(self.combobox_file_1)
        layout_file_selection.addLayout(layout_buttons_file_1)
        layout_file_selection.addWidget(self.label_pick_file_2)
        layout_file_selection.addWidget(self.combobox_file_2)
        layout_file_selection.addLayout(layout_buttons_file_2)
        layout_file_selection.addWidget(label_delete_file)
        layout_file_selection.addWidget(self.combobox_delete_file)
        layout_file_selection.addWidget(button_confirm_delete_file)
        layout_file_selection.addStretch()
        self.setLayout(layout_file_selection)

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

    def select_file_1(self, combo_box: QComboBox):
        selected_csv_path = combo_box.currentData()
        run_file_1 = selected_csv_path
        run_data_1 = pd.read_csv(run_file_1)  # type: ignore
        self.label_pick_file_1.setText(f"Select First Run (selected: {combo_box.currentText()})")
        self.run_1_updated.emit(run_data_1)

    def select_file_2(self, combo_box: QComboBox):
        selected_csv_path = combo_box.currentData()
        run_file_2 = selected_csv_path
        run_data_2 = pd.read_csv(run_file_2)  # type: ignore
        self.label_pick_file_2.setText(f"Select Second Run (selected: {combo_box.currentText()})")
        self.run_2_updated.emit(run_data_2)

    def clear_file_1(self):
        self.label_pick_file_1.setText("Select First Run")
        self.run_1_updated.emit(None)

    def clear_file_2(self):
        self.label_pick_file_2.setText("Select Second Run")
        self.run_1_updated.emit(None)

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
            self, "Success", f"Run '{selected_name}' has been deleted. The software has been reset."
        )
        self.clear_file_1()
        self.clear_file_2()
        self.run_1_updated.emit(None)
        self.run_2_updated.emit(None)



class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 300)
        self._build_ui()

    def _build_ui(self):
        layout_option_selection = QVBoxLayout()
        layout_option_selection.setContentsMargins(24, 24, 24, 24)
        layout_option_selection.setSpacing(10)

        label_select_options = QLabel("Select Visible Datapoints")
        checkbox_layout_1 = QHBoxLayout()
        checkbox_track_map = QCheckBox("Track Map")
        checkbox_file_1_heatmap = QCheckBox("Run 1 Speed Heatmap")
        checkbox_layout_1.addWidget(checkbox_track_map)
        checkbox_layout_1.addWidget(checkbox_file_1_heatmap)
        checkbox_layout_2 = QHBoxLayout()
        checkbox_file_2_heatmap = QCheckBox("Run 2 Speed Heatmap")
        checkbox_radius = QCheckBox("Radius")
        checkbox_layout_2.addWidget(checkbox_file_2_heatmap)
        checkbox_layout_2.addWidget(checkbox_radius)
        checkbox_layout_3 = QHBoxLayout()
        checkbox_file_1_g = QCheckBox("Run 1 G Forces")
        checkbox_file_2_g = QCheckBox("Run 2 G Forces")
        checkbox_layout_3.addWidget(checkbox_file_1_g)
        checkbox_layout_3.addWidget(checkbox_file_2_g)
        checkbox_layout_4 = QHBoxLayout()
        checkbox_steering_angle = QCheckBox("Steering Angle")
        checkbox_acceleration_prs = QCheckBox("Acceleration Pressure")
        checkbox_layout_4.addWidget(checkbox_steering_angle)
        checkbox_layout_4.addWidget(checkbox_acceleration_prs)
        checkbox_layout_5 = QHBoxLayout()
        checkbox_brake_prs = QCheckBox("Brake Pressure")
        checkbox_yaw_vel = QCheckBox("Yaw Velocity")
        checkbox_layout_5.addWidget(checkbox_yaw_vel)
        checkbox_layout_5.addWidget(checkbox_brake_prs)
        checkbox_layout_6 = QHBoxLayout()
        checkbox_yaw_acc = QCheckBox("Yaw Acceleration")
        checkbox_slip_angle = QCheckBox("Slip Angle")
        checkbox_layout_6.addWidget(checkbox_yaw_acc)
        checkbox_layout_6.addWidget(checkbox_slip_angle)
        checkbox_layout_7 = QHBoxLayout()
        checkbox_slip_ratio = QCheckBox("Slip Ratio")
        checkbox_tire_fy = QCheckBox("Tire Fy")
        checkbox_layout_7.addWidget(checkbox_slip_ratio)
        checkbox_layout_7.addWidget(checkbox_tire_fy)
        checkbox_layout_8 = QHBoxLayout()
        checkbox_roll_grad = QCheckBox("Roll Gradient")
        checkbox_pitch_grad = QCheckBox("Pitch Gradient")
        checkbox_layout_8.addWidget(checkbox_roll_grad)
        checkbox_layout_8.addWidget(checkbox_pitch_grad)
        checkbox_layout_9 = QHBoxLayout()
        checkbox_beta = QCheckBox("Beta")
        checkbox_battery_power = QCheckBox("Battery Power")
        checkbox_layout_9.addWidget(checkbox_beta)
        checkbox_layout_9.addWidget(checkbox_battery_power)
        checkbox_layout_10 = QHBoxLayout()
        checkbox_power_draw = QCheckBox("Power Draw")
        checkbox_layout_10.addWidget(checkbox_power_draw)

        layout_option_selection.addWidget(label_select_options)
        layout_option_selection.addLayout(checkbox_layout_1)
        layout_option_selection.addLayout(checkbox_layout_2)
        layout_option_selection.addLayout(checkbox_layout_3)
        layout_option_selection.addLayout(checkbox_layout_4)
        layout_option_selection.addLayout(checkbox_layout_5)
        layout_option_selection.addLayout(checkbox_layout_6)
        layout_option_selection.addLayout(checkbox_layout_7)
        layout_option_selection.addLayout(checkbox_layout_8)
        layout_option_selection.addLayout(checkbox_layout_9)
        layout_option_selection.addLayout(checkbox_layout_10)
        layout_option_selection.addStretch()

        self.setLayout(layout_option_selection)



class DataWindow(QWidget):
    show_track_map = False
    show_run_1_speed_heatmap = False
    show_run_2_speed_heatmap = False
    show_radius = False
    show_run_1_g = False
    show_run_2_g = False
    show_steering_angle = False
    show_acceleration_prs = False
    show_brake_prs = False
    show_yaw_vel = False
    show_yaw_acc = False
    show_slip_angle = False
    show_slip_ratio = False
    show_tire_fy = False
    show_roll_grad = False
    show_pitch_grad = False
    show_beta = False
    show_battery_power = False
    show_power_draw = False

    slider: QSlider
    label_slider: QLabel
    button_slider: QPushButton
    TIME_SCALE = 100
    is_slider_playing = False
    playback_timer: QTimer

    def __init__(self):
        super().__init__()
        self.setMinimumSize(750, 500)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout_slider = QHBoxLayout()
        self.button_slider = QPushButton("Play")
        self.button_slider.clicked.connect(self._on_slider_play)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.label_slider = QLabel("0.00 s")
        layout_slider.addWidget(self.button_slider)
        layout_slider.addWidget(self.slider)
        layout_slider.addWidget(self.label_slider)
        layout.addLayout(layout_slider)

        self.playback_timer = QTimer(self)
        self.playback_timer.setInterval(16)
        self.playback_timer.timeout.connect(self._sync_to_clock)

        self._play_start_real_time: float = 0.0
        self._slider_start_value: int = 0
        self.playback_speed: float = 1.0
        self.ticks_per_second: float = 100.0

        layout.addStretch()
        self.setLayout(layout)

    def update_slider_max(self, max_value: int):
        if self.slider is not None:
            self.slider.setMaximum(max_value * self.TIME_SCALE)
            self.slider.setEnabled(max_value > 0)

    def _on_slider_changed(self, value: int):
        seconds = value / self.TIME_SCALE
        if self.label_slider is not None:
            self.label_slider.setText(f"{seconds:.2f} s")

    def _on_slider_play(self):
        if self.playback_timer.isActive():
            self.playback_timer.stop()
        else:
            if self.slider.value() >= self.slider.maximum():
                self.slider.setValue(0)

            self._play_start_real_time = time.perf_counter()
            self._slider_start_value = self.slider.value()
            self.playback_timer.start()

        self.is_slider_playing = not self.is_slider_playing
        if self.is_slider_playing:
            self.button_slider.setText("Pause")
        else:
            self.button_slider.setText("Play")

    def _step_forward(self):
        current = self.slider.value()
        maximum = self.slider.maximum()

        if current < maximum:
            self.slider.setValue(current + 1)
        else:
            self.playback_timer.stop()

    def _sync_to_clock(self):
        elapsed_real_seconds = time.perf_counter() - self._play_start_real_time
        target_ticks = (
                elapsed_real_seconds * self.ticks_per_second * self.playback_speed
        )
        new_value = int(self._slider_start_value + target_ticks)

        if new_value < self.slider.maximum():
            self.slider.setValue(new_value)
        else:
            self.slider.setValue(self.slider.maximum())
            self.playback_timer.stop()




class FileAdditionWindow(QWidget):
    file_to_add = None
    label_current_selected = None
    textbox_name = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle(window_titles[1])
        self.setFixedSize(QSize(500, 200))
        self.setMinimumSize(QSize(500, 200))
        self.setMaximumSize(QSize(500, 200))
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
        layout.addStretch()
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