import math
import sys
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel, QFileDialog, \
    QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QSplitter, QCheckBox, QSlider, QScrollArea

import json
import shutil
import uuid
from pathlib import Path

from scipy.signal import savgol_filter

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

plt.style.use('dark_background')


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
        self.window_options.show_track_map.connect(
            lambda state: self.handle_track_map(state)
        )
        self.window_options.show_run_1_speed_heatmap.connect(
            lambda state: self.handle_file_1_heatmap(state)
        )
        self.window_options.show_run_2_speed_heatmap.connect(
            lambda state: self.handle_file_2_heatmap(state)
        )
        self.window_options.show_speed.connect(
            lambda state: self.handle_speed(state)
        )
        self.window_options.show_radius.connect(
            lambda state: self.handle_radius(state)
        )
        self.window_options.show_run_1_g.connect(
            lambda state: self.handle_file_1_g(state)
        )
        self.window_options.show_run_2_g.connect(
            lambda state: self.handle_file_2_g(state)
        )
        self.window_options.show_steering_angle.connect(
            lambda state: self.handle_steering_angle(state)
        )
        self.window_options.show_acceleration_prs.connect(
            lambda state: self.handle_acceleration_prs(state)
        )
        self.window_options.show_brake_prs.connect(
            lambda state: self.handle_brake_prs(state)
        )
        self.window_options.show_yaw_vel.connect(
            lambda state: self.handle_yaw_vel(state)
        )
        self.window_options.show_yaw_acc.connect(
            lambda state: self.handle_yaw_acc(state)
        )
        self.window_options.show_slip_angle.connect(
            lambda state: self.handle_slip_angle(state)
        )
        self.window_options.show_slip_ratio.connect(
            lambda state: self.handle_slip_ratio(state)
        )
        self.window_options.show_tire_fy.connect(
            lambda state: self.handle_tire_fy(state)
        )
        self.window_options.show_roll_grad.connect(
            lambda state: self.handle_roll_grad(state)
        )
        self.window_options.show_pitch_grad.connect(
            lambda state: self.handle_pitch_grad(state)
        )
        self.window_options.show_beta.connect(
            lambda state: self.handle_beta(state)
        )
        self.window_options.show_battery_power.connect(
            lambda state: self.handle_battery_power(state)
        )
        self.window_options.show_power_draw.connect(
            lambda state: self.handle_power_draw(state)
        )

    def _build_stats_ui(self):
        self.splitter_data.addWidget(QWidget())

    def handle_run_1_update(self, df: pd.DataFrame | None):
        self.active_run_1 = df
        self.rework_slider()
        self.window_options.reemit_signals()

    def handle_run_2_update(self, df: pd.DataFrame | None):
        self.active_run_2 = df
        self.rework_slider()
        self.window_options.reemit_signals()

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

    def handle_track_map(self, to_build: bool):
        if to_build:
            self.window_data.build_track_map(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_track_map()

    def handle_file_1_heatmap(self, to_build: bool):
        if to_build:
            self.window_data.build_file_1_heatmap(self.active_run_1)
        else:
            self.window_data.destroy_file_1_heatmap()

    def handle_file_2_heatmap(self, to_build: bool):
        if to_build:
            self.window_data.build_file_2_heatmap(self.active_run_2)
        else:
            self.window_data.destroy_file_2_heatmap()

    def handle_speed(self, to_build: bool):
        if to_build:
            self.window_data.build_speed(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_speed()

    def handle_radius(self, to_build: bool):
        if to_build:
            self.window_data.build_radius(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_radius()

    def handle_file_1_g(self, to_build: bool):
        if to_build:
            self.window_data.build_file_1_g(self.active_run_1)
        else:
            self.window_data.destroy_file_1_g()

    def handle_file_2_g(self, to_build: bool):
        if to_build:
            self.window_data.build_file_2_g(self.active_run_2)
        else:
            self.window_data.destroy_file_2_g()

    def handle_steering_angle(self, to_build: bool):
        if to_build:
            self.window_data.build_steering_angle(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_steering_angle()

    def handle_acceleration_prs(self, to_build: bool):
        if to_build:
            self.window_data.build_acceleration_prs(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_acceleration_prs()

    def handle_brake_prs(self, to_build: bool):
        if to_build:
            self.window_data.build_brake_prs(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_brake_prs()

    def handle_yaw_vel(self, to_build: bool):
        if to_build:
            self.window_data.build_yaw_vel(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_yaw_vel()

    def handle_yaw_acc(self, to_build: bool):
        if to_build:
            self.window_data.build_yaw_acc(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_yaw_acc()

    def handle_slip_angle(self, to_build: bool):
        if to_build:
            self.window_data.build_slip_angle(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_slip_angle()

    def handle_slip_ratio(self, to_build: bool):
        if to_build:
            self.window_data.build_slip_ratio(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_slip_ratio()

    def handle_tire_fy(self, to_build: bool):
        if to_build:
            self.window_data.build_tire_fy(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_tire_fy()

    def handle_roll_grad(self, to_build: bool):
        if to_build:
            self.window_data.build_roll_grad(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_roll_grad()

    def handle_pitch_grad(self, to_build: bool):
        if to_build:
            self.window_data.build_pitch_grad(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_pitch_grad()

    def handle_beta(self, to_build: bool):
        if to_build:
            self.window_data.build_beta(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_beta()

    def handle_battery_power(self, to_build: bool):
        if to_build:
            self.window_data.build_battery_power(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_battery_power()

    def handle_power_draw(self, to_build: bool):
        if to_build:
            self.window_data.build_power_draw(self.active_run_1, self.active_run_2)
        else:
            self.window_data.destroy_power_draw()




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
        self.run_2_updated.emit(None)

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
    show_track_map = pyqtSignal(bool)
    show_run_1_speed_heatmap = pyqtSignal(bool)
    show_run_2_speed_heatmap = pyqtSignal(bool)
    show_speed = pyqtSignal(bool)
    show_radius = pyqtSignal(bool)
    show_run_1_g = pyqtSignal(bool)
    show_run_2_g = pyqtSignal(bool)
    show_steering_angle = pyqtSignal(bool)
    show_acceleration_prs = pyqtSignal(bool)
    show_brake_prs = pyqtSignal(bool)
    show_yaw_vel = pyqtSignal(bool)
    show_yaw_acc = pyqtSignal(bool)
    show_slip_angle = pyqtSignal(bool)
    show_slip_ratio = pyqtSignal(bool)
    show_tire_fy = pyqtSignal(bool)
    show_roll_grad = pyqtSignal(bool)
    show_pitch_grad = pyqtSignal(bool)
    show_beta = pyqtSignal(bool)
    show_battery_power = pyqtSignal(bool)
    show_power_draw = pyqtSignal(bool)

    checkbox_track_map: QCheckBox
    checkbox_file_1_heatmap: QCheckBox
    checkbox_file_2_heatmap: QCheckBox
    checkbox_speed: QCheckBox
    checkbox_radius: QCheckBox
    checkbox_file_1_g: QCheckBox
    checkbox_file_2_g: QCheckBox
    checkbox_steering_angle: QCheckBox
    checkbox_acceleration_prs: QCheckBox
    checkbox_brake_prs: QCheckBox
    checkbox_yaw_vel: QCheckBox
    checkbox_yaw_acc: QCheckBox
    checkbox_slip_angle: QCheckBox
    checkbox_slip_ratio: QCheckBox
    checkbox_tire_fy: QCheckBox
    checkbox_roll_grad: QCheckBox
    checkbox_pitch_grad: QCheckBox
    checkbox_beta: QCheckBox
    checkbox_battery_power: QCheckBox
    checkbox_power_draw: QCheckBox

    layout_option_selection: QVBoxLayout

    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 300)
        self._build_ui()

    def _build_ui(self):
        self.layout_option_selection = QVBoxLayout()
        self.layout_option_selection.setContentsMargins(24, 24, 24, 24)
        self.layout_option_selection.setSpacing(10)

        label_select_options = QLabel("Select Visible Datapoints")
        checkbox_layout_1 = QHBoxLayout()
        self.checkbox_track_map = QCheckBox("Track Map")
        self.checkbox_track_map.stateChanged.connect(self.signal_track_map)
        self.checkbox_file_1_heatmap = QCheckBox("Run 1 Speed Heatmap")
        self.checkbox_file_1_heatmap.stateChanged.connect(self.signal_run_1_speed_heatmap)
        checkbox_layout_1.addWidget(self.checkbox_track_map)
        checkbox_layout_1.addWidget(self.checkbox_file_1_heatmap)
        checkbox_layout_2 = QHBoxLayout()
        self.checkbox_file_2_heatmap = QCheckBox("Run 2 Speed Heatmap")
        self.checkbox_file_2_heatmap.stateChanged.connect(self.signal_run_2_speed_heatmap)
        self.checkbox_speed = QCheckBox("Speed")
        self.checkbox_speed.stateChanged.connect(self.signal_speed)
        checkbox_layout_2.addWidget(self.checkbox_file_2_heatmap)
        checkbox_layout_2.addWidget(self.checkbox_speed)
        checkbox_layout_3 = QHBoxLayout()
        self.checkbox_radius = QCheckBox("Radius")
        self.checkbox_radius.stateChanged.connect(self.signal_radius)
        self.checkbox_file_1_g = QCheckBox("Run 1 G Forces")
        self.checkbox_file_1_g.stateChanged.connect(self.signal_run_1_g)
        checkbox_layout_3.addWidget(self.checkbox_radius)
        checkbox_layout_3.addWidget(self.checkbox_file_1_g)
        checkbox_layout_4 = QHBoxLayout()
        self.checkbox_file_2_g = QCheckBox("Run 2 G Forces")
        self.checkbox_file_2_g.stateChanged.connect(self.signal_run_2_g)
        self.checkbox_steering_angle = QCheckBox("Steering Angle")
        self.checkbox_steering_angle.stateChanged.connect(self.signal_steering_angle)
        checkbox_layout_4.addWidget(self.checkbox_file_2_g)
        checkbox_layout_4.addWidget(self.checkbox_steering_angle)
        checkbox_layout_5 = QHBoxLayout()
        self.checkbox_acceleration_prs = QCheckBox("Acceleration Pressure")
        self.checkbox_acceleration_prs.stateChanged.connect(self.signal_acceleration_prs)
        self.checkbox_yaw_vel = QCheckBox("Yaw Velocity")
        self.checkbox_yaw_vel.stateChanged.connect(self.signal_yaw_vel)
        checkbox_layout_5.addWidget(self.checkbox_acceleration_prs)
        checkbox_layout_5.addWidget(self.checkbox_yaw_vel)
        checkbox_layout_6 = QHBoxLayout()
        self.checkbox_brake_prs = QCheckBox("Brake Pressure")
        self.checkbox_brake_prs.stateChanged.connect(self.signal_brake_prs)
        self.checkbox_yaw_acc = QCheckBox("Yaw Acceleration")
        self.checkbox_yaw_acc.stateChanged.connect(self.signal_yaw_acc)
        checkbox_layout_6.addWidget(self.checkbox_brake_prs)
        checkbox_layout_6.addWidget(self.checkbox_yaw_acc)
        checkbox_layout_7 = QHBoxLayout()
        self.checkbox_slip_angle = QCheckBox("Slip Angle")
        self.checkbox_slip_angle.stateChanged.connect(self.signal_slip_angle)
        self.checkbox_slip_ratio = QCheckBox("Slip Ratio")
        self.checkbox_slip_ratio.stateChanged.connect(self.signal_slip_ratio)
        checkbox_layout_7.addWidget(self.checkbox_slip_angle)
        checkbox_layout_7.addWidget(self.checkbox_slip_ratio)
        checkbox_layout_8 = QHBoxLayout()
        self.checkbox_tire_fy = QCheckBox("Tire Fy")
        self.checkbox_tire_fy.stateChanged.connect(self.signal_tire_fy)
        self.checkbox_roll_grad = QCheckBox("Roll Gradient")
        self.checkbox_roll_grad.stateChanged.connect(self.signal_roll_grad)
        checkbox_layout_8.addWidget(self.checkbox_tire_fy)
        checkbox_layout_8.addWidget(self.checkbox_roll_grad)
        checkbox_layout_9 = QHBoxLayout()
        self.checkbox_pitch_grad = QCheckBox("Pitch Gradient")
        self.checkbox_pitch_grad.stateChanged.connect(self.signal_pitch_grad)
        self.checkbox_beta = QCheckBox("Beta")
        self.checkbox_beta.stateChanged.connect(self.signal_beta)
        checkbox_layout_9.addWidget(self.checkbox_pitch_grad)
        checkbox_layout_9.addWidget(self.checkbox_beta)
        checkbox_layout_10 = QHBoxLayout()
        self.checkbox_battery_power = QCheckBox("Battery Power")
        self.checkbox_battery_power.stateChanged.connect(self.signal_battery_power)
        self.checkbox_power_draw = QCheckBox("Power Draw")
        self.checkbox_power_draw.stateChanged.connect(self.signal_power_draw)
        checkbox_layout_10.addWidget(self.checkbox_battery_power)
        checkbox_layout_10.addWidget(self.checkbox_power_draw)

        self.layout_option_selection.addWidget(label_select_options)
        self.layout_option_selection.addLayout(checkbox_layout_1)
        self.layout_option_selection.addLayout(checkbox_layout_2)
        self.layout_option_selection.addLayout(checkbox_layout_3)
        self.layout_option_selection.addLayout(checkbox_layout_4)
        self.layout_option_selection.addLayout(checkbox_layout_5)
        self.layout_option_selection.addLayout(checkbox_layout_6)
        self.layout_option_selection.addLayout(checkbox_layout_7)
        self.layout_option_selection.addLayout(checkbox_layout_8)
        self.layout_option_selection.addLayout(checkbox_layout_9)
        self.layout_option_selection.addLayout(checkbox_layout_10)
        self.layout_option_selection.addStretch()

        self.setLayout(self.layout_option_selection)

    def signal_track_map(self):
        if self.checkbox_track_map.isChecked():
            self.show_track_map.emit(True)
        else:
            self.show_track_map.emit(False)

    def signal_run_1_speed_heatmap(self):
        if self.checkbox_file_1_heatmap.isChecked():
            self.show_run_1_speed_heatmap.emit(True)
        else:
            self.show_run_1_speed_heatmap.emit(False)

    def signal_run_2_speed_heatmap(self):
        if self.checkbox_file_2_heatmap.isChecked():
            self.show_run_2_speed_heatmap.emit(True)
        else:
            self.show_run_2_speed_heatmap.emit(False)

    def signal_speed(self):
        if self.checkbox_speed.isChecked():
            self.show_speed.emit(True)
        else:
            self.show_speed.emit(False)

    def signal_radius(self):
        if self.checkbox_radius.isChecked():
            self.show_radius.emit(True)
        else:
            self.show_radius.emit(False)

    def signal_run_1_g(self):
        if self.checkbox_file_1_g.isChecked():
            self.show_run_1_g.emit(True)
        else:
            self.show_run_1_g.emit(False)

    def signal_run_2_g(self):
        if self.checkbox_file_2_g.isChecked():
            self.show_run_2_g.emit(True)
        else:
            self.show_run_2_g.emit(False)

    def signal_steering_angle(self):
        if self.checkbox_steering_angle.isChecked():
            self.show_steering_angle.emit(True)
        else:
            self.show_steering_angle.emit(False)

    def signal_acceleration_prs(self):
        if self.checkbox_acceleration_prs.isChecked():
            self.show_acceleration_prs.emit(True)
        else:
            self.show_acceleration_prs.emit(False)

    def signal_brake_prs(self):
        if self.checkbox_brake_prs.isChecked():
            self.show_brake_prs.emit(True)
        else:
            self.show_brake_prs.emit(False)

    def signal_yaw_vel(self):
        if self.checkbox_yaw_vel.isChecked():
            self.show_yaw_vel.emit(True)
        else:
            self.show_yaw_vel.emit(False)

    def signal_yaw_acc(self):
        if self.checkbox_yaw_acc.isChecked():
            self.show_yaw_acc.emit(True)
        else:
            self.show_yaw_acc.emit(False)

    def signal_slip_angle(self):
        if self.checkbox_slip_angle.isChecked():
            self.show_slip_angle.emit(True)
        else:
            self.show_slip_angle.emit(False)

    def signal_slip_ratio(self):
        if self.checkbox_slip_ratio.isChecked():
            self.show_slip_ratio.emit(True)
        else:
            self.show_slip_ratio.emit(False)

    def signal_tire_fy(self):
        if self.checkbox_tire_fy.isChecked():
            self.show_tire_fy.emit(True)
        else:
            self.show_tire_fy.emit(False)

    def signal_roll_grad(self):
        if self.checkbox_roll_grad.isChecked():
            self.show_roll_grad.emit(True)
        else:
            self.show_roll_grad.emit(False)

    def signal_pitch_grad(self):
        if self.checkbox_pitch_grad.isChecked():
            self.show_pitch_grad.emit(True)
        else:
            self.show_pitch_grad.emit(False)

    def signal_beta(self):
        if self.checkbox_beta.isChecked():
            self.show_beta.emit(True)
        else:
            self.show_beta.emit(False)

    def signal_battery_power(self):
        if self.checkbox_battery_power.isChecked():
            self.show_battery_power.emit(True)
        else:
            self.show_battery_power.emit(False)

    def signal_power_draw(self):
        if self.checkbox_power_draw.isChecked():
            self.show_power_draw.emit(True)
        else:
            self.show_power_draw.emit(False)

    def reemit_signals(self):
        self.signal_track_map()
        self.signal_run_1_speed_heatmap()
        self.signal_run_2_speed_heatmap()
        self.signal_speed()
        self.signal_radius()
        self.signal_run_1_g()
        self.signal_run_2_g()
        self.signal_steering_angle()
        self.signal_acceleration_prs()
        self.signal_brake_prs()
        self.signal_yaw_vel()
        self.signal_yaw_acc()
        self.signal_slip_angle()
        self.signal_slip_ratio()
        self.signal_tire_fy()
        self.signal_roll_grad()
        self.signal_pitch_grad()
        self.signal_beta()
        self.signal_battery_power()
        self.signal_power_draw()

    def reset_checkboxes(self):
        for i in range(self.layout_option_selection.count()):
            item = self.layout_option_selection.itemAt(i)
            widget = item.widget()      # type: ignore
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)



class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)



class DataWindow(QWidget):
    df1: pd.DataFrame | None = None
    df2: pd.DataFrame | None = None
    layout: QVBoxLayout
    layout_widgets: QVBoxLayout | None = None

    widget_track_map: QWidget | None = None
    track_dot_1 = None
    track_dot_2 = None
    layout_track_map: QVBoxLayout | None = None
    canvas_track_map: MplCanvas | None = None

    widget_file_1_heatmap: QWidget | None = None
    heat_track_dot_1 = None
    layout_file_1_heatmap: QVBoxLayout | None = None
    canvas_file_1_heatmap: MplCanvas | None = None

    widget_file_2_heatmap: QWidget | None = None
    heat_track_dot_2 = None
    layout_file_2_heatmap: QVBoxLayout | None = None
    canvas_file_2_heatmap: MplCanvas | None = None

    widget_file_1_g: QWidget | None = None
    g_dot_1 = None
    layout_file_1_g: QVBoxLayout | None = None
    canvas_file_1_g: MplCanvas | None = None

    widget_file_2_g: QWidget | None = None
    g_dot_2 = None
    layout_file_2_g: QVBoxLayout | None = None
    canvas_file_2_g: MplCanvas | None = None

    active_plots = {}

    widget_speed: QWidget | None = None
    layout_speed: QVBoxLayout | None = None
    canvas_speed: MplCanvas | None = None

    widget_radius: QWidget | None = None
    layout_radius: QVBoxLayout | None = None
    canvas_radius: MplCanvas | None = None

    widget_steering_angle: QWidget | None = None
    layout_steering_angle: QVBoxLayout | None = None
    canvas_steering_angle: MplCanvas | None = None

    widget_acceleration_prs: QWidget | None = None
    layout_acceleration_prs: QVBoxLayout | None = None
    canvas_acceleration_prs: MplCanvas | None = None

    widget_brake_prs: QWidget | None = None
    layout_brake_prs: QVBoxLayout | None = None
    canvas_brake_prs: MplCanvas | None = None

    widget_yaw_vel: QWidget | None = None
    layout_yaw_vel: QVBoxLayout | None = None
    canvas_yaw_vel: MplCanvas | None = None

    widget_yaw_acc: QWidget | None = None
    layout_yaw_acc: QVBoxLayout | None = None
    canvas_yaw_acc: MplCanvas | None = None

    widget_slip_angle: QWidget | None = None
    layout_slip_angle: QVBoxLayout | None = None
    canvas_slip_angle: MplCanvas | None = None

    widget_slip_ratio: QWidget | None = None
    layout_slip_ratio: QVBoxLayout | None = None
    canvas_slip_ratio: MplCanvas | None = None

    widget_tire_fy: QWidget | None = None
    layout_tire_fy: QVBoxLayout | None = None
    canvas_tire_fy: MplCanvas | None = None

    widget_roll_grad: QWidget | None = None
    layout_roll_grad: QVBoxLayout | None = None
    canvas_roll_grad: MplCanvas | None = None

    widget_pitch_grad: QWidget | None = None
    layout_pitch_grad: QVBoxLayout | None = None
    canvas_pitch_grad: MplCanvas | None = None

    widget_beta: QWidget | None = None
    layout_beta: QVBoxLayout | None = None
    canvas_beta: MplCanvas | None = None

    widget_battery_power: QWidget | None = None
    layout_battery_power: QVBoxLayout | None = None
    canvas_battery_power: MplCanvas | None = None

    widget_power_draw: QWidget | None = None
    layout_power_draw: QVBoxLayout | None = None
    canvas_power_draw: MplCanvas | None = None



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
        self.layout = QVBoxLayout()

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
        self.layout.addLayout(layout_slider)

        self.layout_widgets = QVBoxLayout()

        scroll_area_data = QScrollArea()
        scroll_area_data.setWidgetResizable(True)
        scroll_area_data.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area_data.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container_widget = QWidget()
        self.layout_widgets = QVBoxLayout(container_widget)
        scroll_area_data.setWidget(container_widget)
        self.layout_widgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(scroll_area_data)

        self.playback_timer = QTimer(self)
        self.playback_timer.setInterval(16)
        self.playback_timer.timeout.connect(self._sync_to_clock)

        self._play_start_real_time: float = 0.0
        self._slider_start_value: int = 0
        self.playback_speed: float = 1.0
        self.ticks_per_second: float = 100.0

        self.setLayout(self.layout)

    def update_slider_max(self, max_value: int):
        if self.slider is not None:
            self.slider.setMaximum(max_value * self.TIME_SCALE)
            self.slider.setEnabled(max_value > 0)

    def _on_slider_changed(self, value: int):
        seconds = value / self.TIME_SCALE
        if self.label_slider is not None:
            self.label_slider.setText(f"{seconds:.2f} s")
            self.update_dots(seconds)
            self.update_file_1_dot(seconds)
            self.update_file_2_dot(seconds)
            self.update_file_1_g_dot(seconds)
            self.update_file_2_g_dot(seconds)
            self.update_plots(seconds)

    def _on_slider_play(self):
        if self.slider.maximum() == 0:
            return

        self.is_slider_playing = not self.is_slider_playing
        if self.is_slider_playing:
            self.button_slider.setText("Pause")
        else:
            self.button_slider.setText("Play")

        if self.playback_timer.isActive():
            self.playback_timer.stop()
        else:
            if self.slider.value() >= self.slider.maximum():
                self.slider.setValue(0)
                self.is_slider_playing = not self.is_slider_playing

            self._play_start_real_time = time.perf_counter()
            self._slider_start_value = self.slider.value()
            self.playback_timer.start()

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

    def build_track_map(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_track_map()

        if isinstance(df1, pd.DataFrame) or isinstance(df2, pd.DataFrame):
            target_df = df1 if isinstance(df1, pd.DataFrame) else df2
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_track_map = QWidget()
            self.widget_track_map.setMinimumHeight(400)
            self.layout_track_map = QVBoxLayout()
            self.canvas_track_map = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_track_map.axes.scatter(target_df.iloc[:, 0], target_df.iloc[:, 1], color="#FFFFFF", s=20)
            self.canvas_track_map.axes.axis('off')

            self.track_dot_1 = self.canvas_track_map.axes.plot([], [], color="#ff0000", marker="o", markersize=12, zorder=4, animated=True)[0] \
                if isinstance(df1, pd.DataFrame) else None
            self.track_dot_2 = self.canvas_track_map.axes.plot([], [], color="#11ff00", marker="o", markersize=12, zorder=4, animated=True)[0] \
                if isinstance(df2, pd.DataFrame) else None

            self.bg_track_map = None

            def _on_draw(event):
                self.bg_track_map = self.canvas_track_map.copy_from_bbox(
                    self.canvas_track_map.axes.bbox
                )
                if self.track_dot_1:
                    self.canvas_track_map.axes.draw_artist(self.track_dot_1)
                if self.track_dot_2:
                    self.canvas_track_map.axes.draw_artist(self.track_dot_2)

            self.canvas_track_map.mpl_connect("draw_event", _on_draw)
            self.canvas_track_map.draw()
            self.layout_track_map.addWidget(self.canvas_track_map)  # type: ignore

            self.widget_track_map.setLayout(self.layout_track_map) # type: ignore
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_track_map)

    def destroy_track_map(self):
        if self.widget_track_map is not None:
            self.track_dot_1 = None
            self.track_dot_2 = None
            self.canvas_track_map = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_track_map)
            self.widget_track_map.hide()
            self.widget_track_map.deleteLater()
            self.widget_track_map = None

    def build_file_1_heatmap(self, df1: pd.DataFrame | None):
        self.destroy_file_1_heatmap()

        if isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_file_1_heatmap = QWidget()
            self.widget_file_1_heatmap.setMinimumHeight(400)
            self.layout_file_1_heatmap = QVBoxLayout()
            self.canvas_file_1_heatmap = MplCanvas(parent=None, width=5, height=4, dpi=100)
            speed_values = pd.to_numeric(self.df1.iloc[:, 5], errors="coerce")
            scatter_plot = self.canvas_file_1_heatmap.axes.scatter(self.df1.iloc[:, 0], self.df1.iloc[:, 1], c=speed_values, cmap="turbo_r", s=20)
            self.heat_track_dot_1 = self.canvas_file_1_heatmap.axes.plot([], [], color="white", marker="o", markersize=12, zorder=4, animated=True)[0]
            self.canvas_file_1_heatmap.axes.axis('off')

            self.bg_file_1_heatmap = None

            def on_draw(event):
                self.bg_file_1_heatmap = self.canvas_file_1_heatmap.copy_from_bbox(
                    self.canvas_file_1_heatmap.axes.bbox
                )
                if self.heat_track_dot_1:
                    self.canvas_file_1_heatmap.axes.draw_artist(self.heat_track_dot_1)

            self.canvas_file_1_heatmap.mpl_connect("draw_event", on_draw)
            self.canvas_file_1_heatmap.draw()
            self.layout_file_1_heatmap.addWidget(self.canvas_file_1_heatmap) # type: ignore
            self.widget_file_1_heatmap.setLayout(self.layout_file_1_heatmap) # type: ignore
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_file_1_heatmap)

    def destroy_file_1_heatmap(self):
        if self.widget_file_1_heatmap is not None:
            self.heat_track_dot_1 = None
            self.canvas_file_1_heatmap = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_file_1_heatmap)
            self.widget_file_1_heatmap.hide()
            self.widget_file_1_heatmap.deleteLater()
            self.widget_file_1_heatmap = None

    def build_file_2_heatmap(self, df2: pd.DataFrame | None):
        self.destroy_file_2_heatmap()

        if isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_file_2_heatmap = QWidget()
            self.widget_file_2_heatmap.setMinimumHeight(400)
            self.layout_file_2_heatmap = QVBoxLayout()
            self.canvas_file_2_heatmap = MplCanvas(parent=None, width=5, height=4, dpi=100)
            speed_values = pd.to_numeric(self.df2.iloc[:, 5], errors="coerce")
            scatter_plot = self.canvas_file_2_heatmap.axes.scatter(self.df2.iloc[:, 0], self.df2.iloc[:, 1], c=speed_values, cmap="turbo_r", s=20)
            self.heat_track_dot_2 = self.canvas_file_2_heatmap.axes.plot([], [], color="white", marker="o", markersize=12, zorder=4, animated=True)[0]
            self.canvas_file_2_heatmap.axes.axis('off')

            self.bg_file_2_heatmap = None

            def on_draw(event):
                self.bg_file_2_heatmap = self.canvas_file_2_heatmap.copy_from_bbox(
                    self.canvas_file_2_heatmap.axes.bbox
                )
                if self.heat_track_dot_2:
                    self.canvas_file_2_heatmap.axes.draw_artist(self.heat_track_dot_2)

            self.canvas_file_2_heatmap.mpl_connect("draw_event", on_draw)
            self.canvas_file_2_heatmap.draw()
            self.layout_file_2_heatmap.addWidget(self.canvas_file_2_heatmap)  # type: ignore
            self.widget_file_2_heatmap.setLayout(self.layout_file_2_heatmap)  # type: ignore
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_file_2_heatmap)


    def destroy_file_2_heatmap(self):
        if self.widget_file_2_heatmap is not None:
            self.heat_track_dot_2 = None
            self.canvas_file_2_heatmap = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_file_2_heatmap)
            self.widget_file_2_heatmap.hide()
            self.widget_file_2_heatmap.deleteLater()
            self.widget_file_2_heatmap = None

    def update_dots(self, cur_time: float):
        if (
            self.canvas_track_map is None or self.widget_track_map is None or self.bg_track_map is None
        ):
            return

        self.canvas_track_map.restore_region(self.bg_track_map)

        if self.track_dot_1 is not None and self.df1 is not None:
            time_col = pd.to_numeric(self.df1.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
            closest_row = np.nanargmin(np.abs(time_col - float(cur_time)))
            x = self.df1.iloc[closest_row, 0]
            y = self.df1.iloc[closest_row, 1]
            self.track_dot_1.set_data([x], [y]) # type: ignore
            self.canvas_track_map.axes.draw_artist(self.track_dot_1)
        if self.track_dot_2 is not None and self.df2 is not None:
            time_col = pd.to_numeric(self.df2.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
            closest_row = np.nanargmin(np.abs(time_col - float(cur_time)))
            x = self.df2.iloc[closest_row, 0]
            y = self.df2.iloc[closest_row, 1]
            self.track_dot_2.set_data([x], [y]) # type: ignore
            self.canvas_track_map.axes.draw_artist(self.track_dot_2)

        self.canvas_track_map.blit(self.canvas_track_map.axes.bbox)

    def update_file_1_dot(self, cur_time: float):
        if (
            self.canvas_file_1_heatmap is None or self.widget_file_1_heatmap is None or self.bg_file_1_heatmap is None
        ):
            return

        self.canvas_file_1_heatmap.restore_region(self.bg_file_1_heatmap)

        if self.heat_track_dot_1 is not None and self.df1 is not None:
            time_col = pd.to_numeric(self.df1.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
            closest_row = np.nanargmin(np.abs(time_col - float(cur_time)))
            x = self.df1.iloc[closest_row, 0]
            y = self.df1.iloc[closest_row, 1]
            self.heat_track_dot_1.set_data([x], [y])
            self.canvas_file_1_heatmap.axes.draw_artist(self.heat_track_dot_1)

        self.canvas_file_1_heatmap.blit(self.canvas_file_1_heatmap.axes.bbox)

    def update_file_2_dot(self, cur_time: float):
        if(
            self.canvas_file_2_heatmap is None or self.widget_file_2_heatmap is None or self.bg_file_2_heatmap is None
        ):
            return

        self.canvas_file_2_heatmap.restore_region(self.bg_file_2_heatmap)

        if self.heat_track_dot_2 is not None and self.df2 is not None:
            time_col = pd.to_numeric(self.df2.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
            closest_row = np.nanargmin(np.abs(time_col - float(cur_time)))
            x = self.df2.iloc[closest_row, 0]
            y = self.df2.iloc[closest_row, 1]
            self.heat_track_dot_2.set_data([x], [y])
            self.canvas_file_2_heatmap.axes.draw_artist(self.heat_track_dot_2)

        self.canvas_file_2_heatmap.blit(self.canvas_file_2_heatmap.axes.bbox)

    def build_file_1_g(self, df1: pd.DataFrame | None):
        self.destroy_file_1_g()

        if isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_file_1_g = QWidget()
            self.widget_file_1_g.setMinimumHeight(400)
            self.layout_file_1_g = QVBoxLayout()
            self.canvas_file_1_g = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_file_1_g.axes.scatter(self.df1.iloc[:,7], self.df1.iloc[:, 8], color="#180cb9", marker="o", s=10, zorder=0)
            self.canvas_file_1_g.axes.set_title("G-G Plot (File 1)")
            self.canvas_file_1_g.axes.set_xlabel("Lateral Acceleration (g)")
            self.canvas_file_1_g.axes.set_ylabel("Longitudinal Acceleration (g)")
            self.g_dot_1 = self.canvas_file_1_g.axes.plot([], [], color="yellow", marker="o", markersize=12, zorder=4, animated=True)[0]

            self.bg_file_1_g = None

            def on_draw(event):
                self.bg_file_1_g = self.canvas_file_1_g.copy_from_bbox(
                    self.canvas_file_1_g.axes.bbox
                )
                if self.g_dot_1:
                    self.canvas_file_1_g.axes.draw_artist(self.g_dot_1)

            self.canvas_file_1_g.mpl_connect("draw_event", on_draw)
            self.canvas_file_1_g.draw()
            self.layout_file_1_g.addWidget(self.canvas_file_1_g) # type: ignore
            self.widget_file_1_g.setLayout(self.layout_file_1_g) # type: ignore
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_file_1_g)

    def destroy_file_1_g(self):
        if self.widget_file_1_g is not None:
            self.g_dot_1 = None
            self.canvas_file_1_g = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_file_1_g)
            self.widget_file_1_g.hide()
            self.widget_file_1_g.deleteLater()
            self.widget_file_1_g = None

    def update_file_1_g_dot(self, cur_time: float):
        if(
            self.canvas_file_1_g is None or self.widget_file_1_g is None or self.bg_file_1_g is None
        ):
            return

        self.canvas_file_1_g.restore_region(self.bg_file_1_g)

        if self.g_dot_1 is not None and self.df1 is not None:
            time_col = pd.to_numeric(self.df1.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
            closest_row = np.nanargmin(np.abs(time_col - float(cur_time)))
            x = self.df1.iloc[closest_row, 7]
            y = self.df1.iloc[closest_row, 8]
            self.g_dot_1.set_data([x], [y])
            self.canvas_file_1_g.axes.draw_artist(self.g_dot_1)

        self.canvas_file_1_g.blit(self.canvas_file_1_g.axes.bbox)

    def build_file_2_g(self, df2: pd.DataFrame | None):
        self.destroy_file_2_g()

        if isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_file_2_g = QWidget()
            self.widget_file_2_g.setMinimumHeight(400)
            self.layout_file_2_g = QVBoxLayout()
            self.canvas_file_2_g = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_file_2_g.axes.scatter(self.df2.iloc[:, 7], self.df2.iloc[:, 8], color="#5d0bba", marker="o", s=10, zorder=0)
            self.canvas_file_2_g.axes.set_title("G-G Plot (File 2)")
            self.canvas_file_2_g.axes.set_xlabel("Lateral Acceleration (g)")
            self.canvas_file_2_g.axes.set_ylabel("Longitudinal Acceleration (g)")
            self.g_dot_2 = self.canvas_file_2_g.axes.plot([], [], color="yellow", marker="o", markersize=12, zorder=4, animated=True)[0]

            self.bg_file_2_g = None

            def on_draw(event):
                self.bg_file_2_g = self.canvas_file_2_g.copy_from_bbox(
                    self.canvas_file_2_g.axes.bbox
                )
                if self.g_dot_2:
                    self.canvas_file_2_g.axes.draw_artist(self.g_dot_2)

            self.canvas_file_2_g.mpl_connect("draw_event", on_draw)
            self.canvas_file_2_g.draw()
            self.layout_file_2_g.addWidget(self.canvas_file_2_g)  # type: ignore
            self.widget_file_2_g.setLayout(self.layout_file_2_g)  # type: ignore
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_file_2_g)

    def destroy_file_2_g(self):
        if self.widget_file_2_g is not None:
            self.g_dot_2 = None
            self.canvas_file_2_g = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_file_2_g)
            self.widget_file_2_g.hide()
            self.widget_file_2_g.deleteLater()
            self.widget_file_2_g = None

    def update_file_2_g_dot(self, cur_time: float):
        if (
                self.canvas_file_2_g is None or self.widget_file_2_g is None or self.bg_file_2_g is None
        ):
            return

        self.canvas_file_2_g.restore_region(self.bg_file_2_g)

        if self.g_dot_2 is not None and self.df2 is not None:
            time_col = pd.to_numeric(self.df2.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
            closest_row = np.nanargmin(np.abs(time_col - float(cur_time)))
            x = self.df2.iloc[closest_row, 7]
            y = self.df2.iloc[closest_row, 8]
            self.g_dot_2.set_data([x], [y])
            self.canvas_file_2_g.axes.draw_artist(self.g_dot_2)

        self.canvas_file_2_g.blit(self.canvas_file_2_g.axes.bbox)

    def build_speed(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_speed()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_speed = QWidget()
            self.widget_speed.setMinimumHeight(400)
            self.layout_speed = QVBoxLayout()
            self.canvas_speed = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_speed.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 5], color="#0075ff", linewidth=0.5)
            self.canvas_speed.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 5], color="#00afff", linewidth=0.5)
            self.canvas_speed.axes.set_title("Speed")
            self.canvas_speed.axes.set_xlabel("Time (s)")
            self.canvas_speed.axes.set_ylabel("Speed (mph)")
            self.canvas_speed.draw()
            self.layout_speed.addWidget(self.canvas_speed)
            self.widget_speed.setLayout(self.layout_speed)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_speed)

            self.active_plots["speed"] = {"canvas": self.canvas_speed, "axis": self.canvas_speed.axes,
                                          "line": self.canvas_speed.axes.axvline(x=0, color="red", linestyle="-",
                                                                                 linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_speed = QWidget()
            self.widget_speed.setMinimumHeight(400)
            self.layout_speed = QVBoxLayout()
            self.canvas_speed = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_speed.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 5], color="#00afff", linewidth=0.5)
            self.canvas_speed.axes.set_title("Speed")
            self.canvas_speed.axes.set_xlabel("Time (s)")
            self.canvas_speed.axes.set_ylabel("Speed (mph)")
            self.canvas_speed.draw()
            self.layout_speed.addWidget(self.canvas_speed)
            self.widget_speed.setLayout(self.layout_speed)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_speed)

            self.active_plots["speed"] = {"canvas": self.canvas_speed, "line": self.canvas_speed.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}

        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_speed = QWidget()
            self.widget_speed.setMinimumHeight(400)
            self.layout_speed = QVBoxLayout()
            self.canvas_speed = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_speed.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 5], color="#00afff", linewidth=0.5)
            self.canvas_speed.axes.set_title("Speed")
            self.canvas_speed.axes.set_xlabel("Time (s)")
            self.canvas_speed.axes.set_ylabel("Speed (mph)")
            self.canvas_speed.draw()
            self.layout_speed.addWidget(self.canvas_speed)
            self.widget_speed.setLayout(self.layout_speed)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_speed)

            self.active_plots["speed"] = {"canvas": self.canvas_speed, "axis": self.canvas_speed.axes, "line": self.canvas_speed.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        else:
            return

    def destroy_speed(self):
        if self.widget_speed is not None:
            self.canvas_speed = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_speed)
            self.widget_speed.hide()
            self.widget_speed.deleteLater()
            self.widget_speed = None
            self.active_plots.pop("speed", None)

    def build_radius(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_radius()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_radius = QWidget()
            self.widget_radius.setMinimumHeight(400)
            self.layout_radius = QVBoxLayout()
            self.canvas_radius = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_radius.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 6], color="#9b3200", linewidth=0.5)
            self.canvas_radius.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 6], color="#ff9100", linewidth=0.5)
            self.canvas_radius.axes.set_title("Radius")
            self.canvas_radius.axes.set_xlabel("Time (s)")
            self.canvas_radius.axes.set_ylabel("Radius (ft)")
            self.canvas_radius.draw()
            self.layout_radius.addWidget(self.canvas_radius)
            self.widget_radius.setLayout(self.layout_radius)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_radius)

            self.active_plots["radius"] = {"canvas": self.canvas_radius, "axis": self.canvas_radius.axes,
                                           "line": self.canvas_radius.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_radius = QWidget()
            self.widget_radius.setMinimumHeight(400)
            self.layout_radius = QVBoxLayout()
            self.canvas_radius = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_radius.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 6], color="#9b3200", linewidth=0.5)
            self.canvas_radius.axes.set_title("Radius")
            self.canvas_radius.axes.set_xlabel("Time (s)")
            self.canvas_radius.axes.set_ylabel("Radius (ft)")
            self.canvas_radius.draw()
            self.layout_radius.addWidget(self.canvas_radius)
            self.widget_radius.setLayout(self.layout_radius)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_radius)

            self.active_plots["radius"] = {"canvas": self.canvas_radius, "axis": self.canvas_radius.axes,
                                           "line": self.canvas_radius.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_radius = QWidget()
            self.widget_radius.setMinimumHeight(400)
            self.layout_radius = QVBoxLayout()
            self.canvas_radius = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_radius.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 6], color="#9b3200", linewidth=0.5)
            self.canvas_radius.axes.set_title("Radius")
            self.canvas_radius.axes.set_xlabel("Time (s)")
            self.canvas_radius.axes.set_ylabel("Radius (ft)")
            self.canvas_radius.draw()
            self.layout_radius.addWidget(self.canvas_radius)
            self.widget_radius.setLayout(self.layout_radius)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_radius)

            self.active_plots["radius"] = {"canvas": self.canvas_radius, "axis": self.canvas_radius.axes,
                                           "line": self.canvas_radius.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        else:
            return


    def destroy_radius(self):
        if self.widget_radius is not None:
            self.canvas_radius = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_radius)
            self.widget_radius.hide()
            self.widget_radius.deleteLater()
            self.widget_radius = None
            self.active_plots.pop("radius", None)

    def build_steering_angle(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_steering_angle()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_steering_angle = QWidget()
            self.widget_steering_angle.setMinimumHeight(400)
            self.layout_steering_angle = QVBoxLayout()
            self.canvas_steering_angle = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_steering_angle.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 9], color="#878787", linewidth=0.5)
            self.canvas_steering_angle.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 9], color="#ffffff", linewidth=0.5)
            self.canvas_steering_angle.axes.set_title("Steering Angle")
            self.canvas_steering_angle.axes.set_xlabel("Time (s)")
            self.canvas_steering_angle.axes.set_ylabel("Angle (Degrees)")
            self.canvas_steering_angle.draw()
            self.layout_steering_angle.addWidget(self.canvas_steering_angle)
            self.widget_steering_angle.setLayout(self.layout_steering_angle)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_steering_angle)

            self.active_plots["steering_angle"] = {"canvas": self.canvas_steering_angle, "axis": self.canvas_steering_angle.axes,
                                           "line": self.canvas_steering_angle.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_steering_angle = QWidget()
            self.widget_steering_angle.setMinimumHeight(400)
            self.layout_steering_angle = QVBoxLayout()
            self.canvas_steering_angle = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_steering_angle.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 9], color="#ffffff",
                                                 linewidth=0.5)
            self.canvas_steering_angle.axes.set_title("Steering Angle")
            self.canvas_steering_angle.axes.set_xlabel("Time (s)")
            self.canvas_steering_angle.axes.set_ylabel("Angle (Degrees)")
            self.canvas_steering_angle.draw()
            self.layout_steering_angle.addWidget(self.canvas_steering_angle)
            self.widget_steering_angle.setLayout(self.layout_steering_angle)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_steering_angle)

            self.active_plots["steering_angle"] = {"canvas": self.canvas_steering_angle,
                                                   "axis": self.canvas_steering_angle.axes,
                                                   "line": self.canvas_steering_angle.axes.axvline(x=0, color="red",
                                                                                                   linestyle="-",
                                                                                                   linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_steering_angle = QWidget()
            self.widget_steering_angle.setMinimumHeight(400)
            self.layout_steering_angle = QVBoxLayout()
            self.canvas_steering_angle = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_steering_angle.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 9], color="#ffffff",
                                                 linewidth=0.5)
            self.canvas_steering_angle.axes.set_title("Steering Angle")
            self.canvas_steering_angle.axes.set_xlabel("Time (s)")
            self.canvas_steering_angle.axes.set_ylabel("Angle (Degrees)")
            self.canvas_steering_angle.draw()
            self.layout_steering_angle.addWidget(self.canvas_steering_angle)
            self.widget_steering_angle.setLayout(self.layout_steering_angle)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_steering_angle)

            self.active_plots["steering_angle"] = {"canvas": self.canvas_steering_angle,
                                                   "axis": self.canvas_steering_angle.axes,
                                                   "line": self.canvas_steering_angle.axes.axvline(x=0, color="red",
                                                                                                   linestyle="-",
                                                                                                   linewidth=1)}
        else:
            return

    def destroy_steering_angle(self):
        if self.widget_steering_angle is not None:
            self.canvas_steering_angle = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_steering_angle)
            self.widget_steering_angle.hide()
            self.widget_steering_angle.deleteLater()
            self.widget_steering_angle = None
            self.active_plots.pop("steering_angle", None)

    def build_acceleration_prs(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_acceleration_prs()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None
        else:
            return

    def destroy_acceleration_prs(self):
        if self.widget_acceleration_prs is not None:
            self.canvas_acceleration_prs = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_acceleration_prs)
            self.widget_acceleration_prs.hide()
            self.widget_acceleration_prs.deleteLater()
            self.widget_acceleration_prs = None
            self.active_plots.pop("acceleration_prs", None)

    def build_brake_prs(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_brake_prs()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None
        else:
            return

    def destroy_brake_prs(self):
        if self.widget_brake_prs is not None:
            self.canvas_brake_prs = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_brake_prs)
            self.widget_brake_prs.hide()
            self.widget_brake_prs.deleteLater()
            self.widget_brake_prs = None
            self.active_plots.pop("brake_prs", None)

    def build_yaw_vel(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_yaw_vel()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_yaw_vel = QWidget()
            self.widget_yaw_vel.setMinimumHeight(400)
            self.layout_yaw_vel = QVBoxLayout()
            self.canvas_yaw_vel = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_yaw_vel.axes.plot(self.df1.iloc[:, 2], (self.df1.iloc[:, 5] * 1.4667 / self.df1.iloc[:, 6]), color="#610091", linewidth=0.5)
            self.canvas_yaw_vel.axes.plot(self.df2.iloc[:, 2], (self.df2.iloc[:, 5] * 1.4667 / self.df2.iloc[:, 6]), color="#ab00ff", linewidth=0.5)
            self.canvas_yaw_vel.axes.set_title("Yaw Velocity")
            self.canvas_yaw_vel.axes.set_xlabel("Time (s)")
            self.canvas_yaw_vel.axes.set_ylabel("Yaw Velocity (1/s)")
            self.canvas_yaw_vel.draw()
            self.layout_yaw_vel.addWidget(self.canvas_yaw_vel)
            self.widget_yaw_vel.setLayout(self.layout_yaw_vel)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_yaw_vel)

            self.active_plots["yaw_vel"] = {"canvas": self.canvas_yaw_vel, "axis": self.canvas_yaw_vel.axes,
                                           "line": self.canvas_yaw_vel.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_yaw_vel = QWidget()
            self.widget_yaw_vel.setMinimumHeight(400)
            self.layout_yaw_vel = QVBoxLayout()
            self.canvas_yaw_vel = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_yaw_vel.axes.plot(self.df1.iloc[:, 2], (self.df1.iloc[:, 5] * 1.4667 / self.df1.iloc[:, 6]),
                                          color="#ab00ff", linewidth=0.5)
            self.canvas_yaw_vel.axes.set_title("Yaw Velocity")
            self.canvas_yaw_vel.axes.set_xlabel("Time (s)")
            self.canvas_yaw_vel.axes.set_ylabel("Yaw Velocity (1/s)")
            self.canvas_yaw_vel.draw()
            self.layout_yaw_vel.addWidget(self.canvas_yaw_vel)
            self.widget_yaw_vel.setLayout(self.layout_yaw_vel)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_yaw_vel)

            self.active_plots["yaw_vel"] = {"canvas": self.canvas_yaw_vel, "axis": self.canvas_yaw_vel.axes,
                                            "line": self.canvas_yaw_vel.axes.axvline(x=0, color="red", linestyle="-",
                                                                                     linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_yaw_vel = QWidget()
            self.widget_yaw_vel.setMinimumHeight(400)
            self.layout_yaw_vel = QVBoxLayout()
            self.canvas_yaw_vel = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_yaw_vel.axes.plot(self.df2.iloc[:, 2], (self.df2.iloc[:, 5] * 1.4667 / self.df1.iloc[:, 6]),
                                          color="#ab00ff", linewidth=0.5)
            self.canvas_yaw_vel.axes.set_title("Yaw Velocity")
            self.canvas_yaw_vel.axes.set_xlabel("Time (s)")
            self.canvas_yaw_vel.axes.set_ylabel("Yaw Velocity (1/s)")
            self.canvas_yaw_vel.draw()
            self.layout_yaw_vel.addWidget(self.canvas_yaw_vel)
            self.widget_yaw_vel.setLayout(self.layout_yaw_vel)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_yaw_vel)

            self.active_plots["yaw_vel"] = {"canvas": self.canvas_yaw_vel, "axis": self.canvas_yaw_vel.axes,
                                            "line": self.canvas_yaw_vel.axes.axvline(x=0, color="red", linestyle="-",
                                                                                     linewidth=1)}
        else:
            return

    def destroy_yaw_vel(self):
        if self.widget_yaw_vel is not None:
            self.canvas_yaw_vel = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_yaw_vel)
            self.widget_yaw_vel.hide()
            self.widget_yaw_vel.deleteLater()
            self.widget_yaw_vel = None
            self.active_plots.pop("yaw_vel", None)

    def build_yaw_acc(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_yaw_acc()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_yaw_acc = QWidget()
            self.widget_yaw_acc.setMinimumHeight(400)
            self.layout_yaw_acc = QVBoxLayout()
            self.canvas_yaw_acc = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_yaw_acc.axes.axhline(y=0, color="#666666", linewidth=0.8, linestyle="--", zorder=1)

            t1 = self.df1.iloc[:, 2].to_numpy()
            yaw_vel_1 = (
                self.df1.iloc[:, 5] * 1.4667 / self.df1.iloc[:, 6]
            )
            dt1 = np.mean(np.diff(t1))
            yaw_accel_1 = savgol_filter(yaw_vel_1, window_length=15, polyorder=2, deriv=1, delta=dt1)
            self.canvas_yaw_acc.axes.plot(t1, yaw_accel_1, color="#579e00", linewidth=0.5, zorder=3)

            t2 = self.df2.iloc[:, 2].to_numpy()
            yaw_vel_2 = (
                self.df2.iloc[:, 5] * 1.4667 / self.df2.iloc[:, 6]
            )
            dt2 = np.mean(np.diff(t2))
            yaw_accel_2 = savgol_filter(yaw_vel_2, window_length=15, polyorder=2, deriv=1, delta=dt2)
            self.canvas_yaw_acc.axes.plot(t2, yaw_accel_2, color="#8bff00", linewidth=0.5, zorder=3)

            self.canvas_yaw_acc.axes.set_title("Yaw Acceleration")
            self.canvas_yaw_acc.axes.set_xlabel("Time (s)")
            self.canvas_yaw_acc.axes.set_ylabel("Yaw Acceleration (1/s/s)")
            self.canvas_yaw_acc.draw()
            self.layout_yaw_acc.addWidget(self.canvas_yaw_acc)
            self.widget_yaw_acc.setLayout(self.layout_yaw_acc)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_yaw_acc)

            self.active_plots["yaw_acc"] = {"canvas": self.canvas_yaw_acc, "axis": self.canvas_yaw_acc.axes,
                                           "line": self.canvas_yaw_acc.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_yaw_acc = QWidget()
            self.widget_yaw_acc.setMinimumHeight(400)
            self.layout_yaw_acc = QVBoxLayout()
            self.canvas_yaw_acc = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_yaw_acc.axes.axhline(y=0, color="#666666", linewidth=0.8, linestyle="--", zorder=1)

            t1 = self.df1.iloc[:, 2].to_numpy()
            yaw_vel_1 = (
                    self.df1.iloc[:, 5] * 1.4667 / self.df1.iloc[:, 6]
            )
            dt1 = np.mean(np.diff(t1))
            yaw_accel_1 = savgol_filter(yaw_vel_1, window_length=15, polyorder=2, deriv=1, delta=dt1)
            self.canvas_yaw_acc.axes.plot(t1, yaw_accel_1, color="#579e00", linewidth=0.5, zorder=3)

            self.canvas_yaw_acc.axes.set_title("Yaw Acceleration")
            self.canvas_yaw_acc.axes.set_xlabel("Time (s)")
            self.canvas_yaw_acc.axes.set_ylabel("Yaw Acceleration (1/s/s)")
            self.canvas_yaw_acc.draw()
            self.layout_yaw_acc.addWidget(self.canvas_yaw_acc)
            self.widget_yaw_acc.setLayout(self.layout_yaw_acc)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_yaw_acc)

            self.active_plots["yaw_acc"] = {"canvas": self.canvas_yaw_acc, "axis": self.canvas_yaw_acc.axes,
                                            "line": self.canvas_yaw_acc.axes.axvline(x=0, color="red", linestyle="-",
                                                                                     linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_yaw_acc = QWidget()
            self.widget_yaw_acc.setMinimumHeight(400)
            self.layout_yaw_acc = QVBoxLayout()
            self.canvas_yaw_acc = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_yaw_acc.axes.axhline(y=0, color="#666666", linewidth=0.8, linestyle="--", zorder=1)

            t2 = self.df2.iloc[:, 2].to_numpy()
            yaw_vel_2 = (
                    self.df2.iloc[:, 5] * 1.4667 / self.df2.iloc[:, 6]
            )
            dt2 = np.mean(np.diff(t2))
            yaw_accel_2 = savgol_filter(yaw_vel_2, window_length=15, polyorder=2, deriv=1, delta=dt2)
            self.canvas_yaw_acc.axes.plot(t2, yaw_accel_2, color="#8bff00", linewidth=0.5, zorder=3)

            self.canvas_yaw_acc.axes.set_title("Yaw Acceleration")
            self.canvas_yaw_acc.axes.set_xlabel("Time (s)")
            self.canvas_yaw_acc.axes.set_ylabel("Yaw Acceleration (1/s/s)")
            self.canvas_yaw_acc.draw()
            self.layout_yaw_acc.addWidget(self.canvas_yaw_acc)
            self.widget_yaw_acc.setLayout(self.layout_yaw_acc)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_yaw_acc)

            self.active_plots["yaw_acc"] = {"canvas": self.canvas_yaw_acc, "axis": self.canvas_yaw_acc.axes,
                                            "line": self.canvas_yaw_acc.axes.axvline(x=0, color="red", linestyle="-",
                                                                                     linewidth=1)}
        else:
            return

    def destroy_yaw_acc(self):
        if self.widget_yaw_acc is not None:
            self.canvas_yaw_acc = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_yaw_acc)
            self.widget_yaw_acc.hide()
            self.widget_yaw_acc.deleteLater()
            self.widget_yaw_acc = None
            self.active_plots.pop("yaw_acc", None)

    def build_slip_angle(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_slip_angle()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_slip_angle = QWidget()
            self.widget_slip_angle.setMinimumHeight(400)
            self.layout_slip_angle = QVBoxLayout()
            self.canvas_slip_angle = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_slip_angle.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 10], color="#82007d", linewidth=0.5)
            self.canvas_slip_angle.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 11], color="#008c00", linewidth=0.5)
            self.canvas_slip_angle.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 10], color="#ff00f5", linewidth=0.5, label="Front Slip")
            self.canvas_slip_angle.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 11], color="#00ff00", linewidth=0.5, label="Rear Slip")
            self.canvas_slip_angle.axes.set_title("Slip Angle")
            self.canvas_slip_angle.axes.set_xlabel("Time (s)")
            self.canvas_slip_angle.axes.set_ylabel("Slip Angle (deg)")
            self.canvas_slip_angle.axes.legend(loc=1)
            self.canvas_slip_angle.draw()
            self.layout_slip_angle.addWidget(self.canvas_slip_angle)
            self.widget_slip_angle.setLayout(self.layout_slip_angle)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_slip_angle)

            self.active_plots["slip_angle"] = {"canvas": self.canvas_slip_angle, "axis": self.canvas_slip_angle.axes,
                                           "line": self.canvas_slip_angle.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_slip_angle = QWidget()
            self.widget_slip_angle.setMinimumHeight(400)
            self.layout_slip_angle = QVBoxLayout()
            self.canvas_slip_angle = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_slip_angle.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 10], color="#ff00f5", linewidth=0.5,
                                             label="Front Slip")
            self.canvas_slip_angle.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 11], color="#00ff00", linewidth=0.5,
                                             label="Rear Slip")
            self.canvas_slip_angle.axes.set_title("Slip Angle")
            self.canvas_slip_angle.axes.set_xlabel("Time (s)")
            self.canvas_slip_angle.axes.set_ylabel("Slip Angle (deg)")
            self.canvas_slip_angle.axes.legend(loc=1)
            self.canvas_slip_angle.draw()
            self.layout_slip_angle.addWidget(self.canvas_slip_angle)
            self.widget_slip_angle.setLayout(self.layout_slip_angle)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_slip_angle)

            self.active_plots["slip_angle"] = {"canvas": self.canvas_slip_angle, "axis": self.canvas_slip_angle.axes,
                                               "line": self.canvas_slip_angle.axes.axvline(x=0, color="red",
                                                                                           linestyle="-", linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.widget_slip_angle = QWidget()
            self.widget_slip_angle.setMinimumHeight(400)
            self.layout_slip_angle = QVBoxLayout()
            self.canvas_slip_angle = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_slip_angle.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 10], color="#ff00f5", linewidth=0.5,
                                             label="Front Slip")
            self.canvas_slip_angle.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 11], color="#00ff00", linewidth=0.5,
                                             label="Rear Slip")
            self.canvas_slip_angle.axes.set_title("Slip Angle")
            self.canvas_slip_angle.axes.set_xlabel("Time (s)")
            self.canvas_slip_angle.axes.set_ylabel("Slip Angle (deg)")
            self.canvas_slip_angle.axes.legend(loc=1)
            self.canvas_slip_angle.draw()
            self.layout_slip_angle.addWidget(self.canvas_slip_angle)
            self.widget_slip_angle.setLayout(self.layout_slip_angle)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_slip_angle)

            self.active_plots["slip_angle"] = {"canvas": self.canvas_slip_angle, "axis": self.canvas_slip_angle.axes,
                                               "line": self.canvas_slip_angle.axes.axvline(x=0, color="red",
                                                                                           linestyle="-", linewidth=1)}
        else:
            return

    def destroy_slip_angle(self):
        if self.widget_slip_angle is not None:
            self.canvas_slip_angle = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_slip_angle)
            self.widget_slip_angle.hide()
            self.widget_slip_angle.deleteLater()
            self.widget_slip_angle = None
            self.active_plots.pop("slip_angle", None)

    def build_slip_ratio(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_slip_ratio()



    def destroy_slip_ratio(self):
        if self.widget_slip_ratio is not None:
            self.canvas_slip_ratio = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_slip_ratio)
            self.widget_slip_ratio.hide()
            self.widget_slip_ratio.deleteLater()
            self.widget_slip_ratio = None
            self.active_plots.pop("slip_ratio", None)

    def build_tire_fy(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_slip_ratio()

    def destroy_tire_fy(self):
        if self.widget_tire_fy is not None:
            self.canvas_tire_fy = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_tire_fy)
            self.widget_tire_fy.hide()
            self.widget_tire_fy.deleteLater()
            self.widget_tire_fy = None
            self.active_plots.pop("tire_fy", None)

    def build_roll_grad(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_roll_grad()

    def destroy_roll_grad(self):
        if self.widget_roll_grad is not None:
            self.canvas_roll_grad = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_roll_grad)
            self.widget_roll_grad.hide()
            self.widget_roll_grad.deleteLater()
            self.widget_roll_grad = None
            self.active_plots.pop("roll_grad", None)

    def build_pitch_grad(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_pitch_grad()

    def destroy_pitch_grad(self):
        if self.widget_pitch_grad is not None:
            self.canvas_pitch_grad = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_pitch_grad)
            self.widget_pitch_grad.hide()
            self.widget_pitch_grad.deleteLater()
            self.widget_pitch_grad = None
            self.active_plots.pop("pitch_grad", None)

    def build_beta(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_beta()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_beta = QWidget()
            self.widget_beta.setMinimumHeight(400)
            self.layout_beta = QVBoxLayout()
            self.canvas_beta = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_beta.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 12], color="#008a73", linewidth=0.5)
            self.canvas_beta.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 12], color="#00ffd4", linewidth=0.5)
            self.canvas_beta.axes.set_title("Beta")
            self.canvas_beta.axes.set_xlabel("Time (s)")
            self.canvas_beta.axes.set_ylabel("Beta (Degrees)")
            self.canvas_beta.draw()
            self.layout_beta.addWidget(self.canvas_beta)
            self.widget_beta.setLayout(self.layout_beta)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_beta)

            self.active_plots["beta"] = {"canvas": self.canvas_beta, "axis": self.canvas_beta.axes,
                                           "line": self.canvas_beta.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_beta = QWidget()
            self.widget_beta.setMinimumHeight(400)
            self.layout_beta = QVBoxLayout()
            self.canvas_beta = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_beta.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 12], color="#00ffd4", linewidth=0.5)
            self.canvas_beta.axes.set_title("Beta")
            self.canvas_beta.axes.set_xlabel("Time (s)")
            self.canvas_beta.axes.set_ylabel("Beta (Degrees)")
            self.canvas_beta.draw()
            self.layout_beta.addWidget(self.canvas_beta)
            self.widget_beta.setLayout(self.layout_beta)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_beta)

            self.active_plots["beta"] = {"canvas": self.canvas_beta, "axis": self.canvas_beta.axes,
                                         "line": self.canvas_beta.axes.axvline(x=0, color="red", linestyle="-",
                                                                               linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_beta = QWidget()
            self.widget_beta.setMinimumHeight(400)
            self.layout_beta = QVBoxLayout()
            self.canvas_beta = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_beta.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 12], color="#00ffd4", linewidth=0.5)
            self.canvas_beta.axes.set_title("Beta")
            self.canvas_beta.axes.set_xlabel("Time (s)")
            self.canvas_beta.axes.set_ylabel("Beta (Degrees)")
            self.canvas_beta.draw()
            self.layout_beta.addWidget(self.canvas_beta)
            self.widget_beta.setLayout(self.layout_beta)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_beta)

            self.active_plots["beta"] = {"canvas": self.canvas_beta, "axis": self.canvas_beta.axes,
                                         "line": self.canvas_beta.axes.axvline(x=0, color="red", linestyle="-",
                                                                               linewidth=1)}
        else:
            return

    def destroy_beta(self):
        if self.widget_beta is not None:
            self.canvas_beta = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_beta)
            self.widget_beta.hide()
            self.widget_beta.deleteLater()
            self.widget_beta = None
            self.active_plots.pop("beta", None)

    def build_power_draw(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_power_draw()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_power_draw = QWidget()
            self.widget_power_draw.setMinimumHeight(400)
            self.layout_power_draw = QVBoxLayout()
            self.canvas_power_draw = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_power_draw.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 15], color="#909000", linewidth=0.5)
            self.canvas_power_draw.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 15], color="#ffff00", linewidth=0.5)
            self.canvas_power_draw.axes.set_title("Power Draw")
            self.canvas_power_draw.axes.set_xlabel("Time (s)")
            self.canvas_power_draw.axes.set_ylabel("Power Draw (%)")
            self.canvas_power_draw.draw()
            self.layout_power_draw.addWidget(self.canvas_power_draw)
            self.widget_power_draw.setLayout(self.layout_power_draw)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_power_draw)

            self.active_plots["power_draw"] = {"canvas": self.canvas_power_draw, "axis": self.canvas_power_draw.axes,
                                           "line": self.canvas_power_draw.axes.axvline(x=0, color="red", linestyle="-", linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_power_draw = QWidget()
            self.widget_power_draw.setMinimumHeight(400)
            self.layout_power_draw = QVBoxLayout()
            self.canvas_power_draw = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_power_draw.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 15], color="#ffff00", linewidth=0.5)
            self.canvas_power_draw.axes.set_title("Power Draw")
            self.canvas_power_draw.axes.set_xlabel("Time (s)")
            self.canvas_power_draw.axes.set_ylabel("Power Draw (%)")
            self.canvas_power_draw.draw()
            self.layout_power_draw.addWidget(self.canvas_power_draw)
            self.widget_power_draw.setLayout(self.layout_power_draw)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_power_draw)

            self.active_plots["power_draw"] = {"canvas": self.canvas_power_draw, "axis": self.canvas_power_draw.axes,
                                               "line": self.canvas_power_draw.axes.axvline(x=0, color="red",
                                                                                           linestyle="-", linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_power_draw = QWidget()
            self.widget_power_draw.setMinimumHeight(400)
            self.layout_power_draw = QVBoxLayout()
            self.canvas_power_draw = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_power_draw.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 15], color="#ffff00", linewidth=0.5)
            self.canvas_power_draw.axes.set_title("Power Draw")
            self.canvas_power_draw.axes.set_xlabel("Time (s)")
            self.canvas_power_draw.axes.set_ylabel("Power Draw (%)")
            self.canvas_power_draw.draw()
            self.layout_power_draw.addWidget(self.canvas_power_draw)
            self.widget_power_draw.setLayout(self.layout_power_draw)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_power_draw)

            self.active_plots["power_draw"] = {"canvas": self.canvas_power_draw, "axis": self.canvas_power_draw.axes,
                                               "line": self.canvas_power_draw.axes.axvline(x=0, color="red",
                                                                                           linestyle="-", linewidth=1)}
        else:
            return


    def destroy_power_draw(self):
        if self.widget_power_draw is not None:
            self.canvas_power_draw = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_power_draw)
            self.widget_power_draw.hide()
            self.widget_power_draw.deleteLater()
            self.widget_power_draw = None
            self.active_plots.pop("power_draw", None)

    def build_battery_power(self, df1: pd.DataFrame | None, df2: pd.DataFrame | None):
        self.destroy_battery_power()

        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_battery_power = QWidget()
            self.widget_battery_power.setMinimumHeight(400)
            self.layout_battery_power = QVBoxLayout()
            self.canvas_battery_power = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_battery_power.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 13], color="#872f00",
                                                 linewidth=0.5)
            self.canvas_battery_power.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 13], color="#ff3d00",
                                                 linewidth=0.5)
            self.canvas_battery_power.axes.set_title("Battery Power")
            self.canvas_battery_power.axes.set_xlabel("Time (s)")
            self.canvas_battery_power.axes.set_ylabel("Battery Power (kW)")
            self.canvas_battery_power.draw()
            self.layout_battery_power.addWidget(self.canvas_battery_power)
            self.widget_battery_power.setLayout(self.layout_battery_power)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_battery_power)

            self.active_plots["battery_power"] = {"canvas": self.canvas_battery_power,
                                                   "axis": self.canvas_battery_power.axes,
                                                   "line": self.canvas_battery_power.axes.axvline(x=0, color="red",
                                                                                                   linestyle="-",
                                                                                                   linewidth=1)}
        elif isinstance(df1, pd.DataFrame):
            self.df1 = df1 if isinstance(df1, pd.DataFrame) else None

            self.widget_battery_power = QWidget()
            self.widget_battery_power.setMinimumHeight(400)
            self.layout_battery_power = QVBoxLayout()
            self.canvas_battery_power = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_battery_power.axes.plot(self.df1.iloc[:, 2], self.df1.iloc[:, 13], color="#ff3d00",
                                                linewidth=0.5)
            self.canvas_battery_power.axes.set_title("Battery Power")
            self.canvas_battery_power.axes.set_xlabel("Time (s)")
            self.canvas_battery_power.axes.set_ylabel("Battery Power (kW)")
            self.canvas_battery_power.draw()
            self.layout_battery_power.addWidget(self.canvas_battery_power)
            self.widget_battery_power.setLayout(self.layout_battery_power)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_battery_power)

            self.active_plots["battery_power"] = {"canvas": self.canvas_battery_power,
                                                  "axis": self.canvas_battery_power.axes,
                                                  "line": self.canvas_battery_power.axes.axvline(x=0, color="red",
                                                                                                 linestyle="-",
                                                                                                 linewidth=1)}
        elif isinstance(df2, pd.DataFrame):
            self.df2 = df2 if isinstance(df2, pd.DataFrame) else None

            self.widget_battery_power = QWidget()
            self.widget_battery_power.setMinimumHeight(400)
            self.layout_battery_power = QVBoxLayout()
            self.canvas_battery_power = MplCanvas(parent=None, width=5, height=4, dpi=100)
            self.canvas_battery_power.axes.plot(self.df2.iloc[:, 2], self.df2.iloc[:, 13], color="#ff3d00",
                                                linewidth=0.5)
            self.canvas_battery_power.axes.set_title("Battery Power")
            self.canvas_battery_power.axes.set_xlabel("Time (s)")
            self.canvas_battery_power.axes.set_ylabel("Battery Power (kW)")
            self.canvas_battery_power.draw()
            self.layout_battery_power.addWidget(self.canvas_battery_power)
            self.widget_battery_power.setLayout(self.layout_battery_power)
            if self.layout_widgets is not None:
                self.layout_widgets.addWidget(self.widget_battery_power)

            self.active_plots["battery_power"] = {"canvas": self.canvas_battery_power,
                                                  "axis": self.canvas_battery_power.axes,
                                                  "line": self.canvas_battery_power.axes.axvline(x=0, color="red",
                                                                                                 linestyle="-",
                                                                                                 linewidth=1)}
        else:
            return

    def destroy_battery_power(self):
        if self.widget_battery_power is not None:
            self.canvas_battery_power = None
            if self.layout_widgets is not None:
                self.layout_widgets.removeWidget(self.widget_battery_power)
            self.widget_battery_power.hide()
            self.widget_battery_power.deleteLater()
            self.widget_battery_power = None
            self.active_plots.pop("battery_power", None)

    def update_plots(self, val: float):
        val = float(val)
        x_min = max(0.0, val-4.0)
        window_size = 8.0
        x_max = x_min + window_size

        for plot in self.active_plots.values():
            canvas = plot["canvas"]
            line = plot.get("line")

            if line is not None:
                line.set_xdata([val, val])
            canvas.axes.set_xlim(x_min, x_max)
            canvas.draw_idle()





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
        run_file = self.file_to_add[0] if (self.file_to_add and self.file_to_add[0]) else None
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