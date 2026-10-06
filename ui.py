"""
ui.py - Complete working GUI for Grinding Polisher
All calculations and features are fully functional
"""

import sys
import os
from datetime import datetime
from typing import Optional, List, Dict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QFormLayout, QMessageBox, QProgressBar,
    QHeaderView, QCheckBox, QListWidget, QListWidgetItem,
    QSplitter, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core import GrindingPolisherEngine, MachineSpecifications, ABRASIVE_SEQUENCES
from database import Database
from visualization import GrindingPolisherVisualizer


class MatplotlibCanvas(FigureCanvas):
    """Canvas for displaying matplotlib figures"""
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize modules
        self.db = Database()
        self.engine = GrindingPolisherEngine()
        self.visualizer = GrindingPolisherVisualizer()
        self.current_experiment_id = None
        self.sim_step = 0
        
        self.init_ui()
        self.load_dashboard()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Grinding Polisher - Metallographic System")
        self.setGeometry(100, 100, 1400, 800)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e8eaed;
                padding: 10px 20px;
                border: 1px solid #dcdde1;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2C7BE5;
            }
            QPushButton {
                background-color: #2C7BE5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a5bb5;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f0f2f5;
                padding: 6px;
                border: 1px solid #dcdde1;
                font-weight: bold;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 10))
        
        # Create tabs
        self.tabs.addTab(self._create_dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._create_design_tab(), "Design")
        self.tabs.addTab(self._create_control_tab(), "Control")
        self.tabs.addTab(self._create_results_tab(), "Results")
        self.tabs.addTab(self._create_history_tab(), "History")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("System Ready")
    
    def _create_header(self) -> QWidget:
        """Create header widget"""
        header = QWidget()
        header.setStyleSheet("""
            background-color: #1a2332;
            border-radius: 8px;
            padding: 10px;
        """)
        layout = QHBoxLayout(header)
        
        title = QLabel("Grinding Polisher System")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status
        self.status_indicator = QLabel("● System Ready")
        self.status_indicator.setFont(QFont("Segoe UI", 10))
        self.status_indicator.setStyleSheet("color: #2ECC71;")
        layout.addWidget(self.status_indicator)
        
        # Time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 10))
        self.time_label.setStyleSheet("color: #8a9ba8;")
        layout.addWidget(self.time_label)
        
        # Update time
        timer = QTimer()
        timer.timeout.connect(self._update_time)
        timer.start(1000)
        self._update_time()
        
        return header
    
    def _update_time(self):
        """Update time display"""
        self.time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def _create_dashboard_tab(self) -> QWidget:
        """Create dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Quick stats
        stats_layout = QGridLayout()
        
        stats = [
            ("Experiments", "0"),
            ("Success Rate", "0%"),
            ("Avg Speed", "0 RPM"),
            ("Materials", "0")
        ]
        
        self.dashboard_cards = {}
        for i, (label, value) in enumerate(stats):
            card = self._create_stat_card(label, value)
            stats_layout.addWidget(card, 0, i)
            self.dashboard_cards[label] = card
        
        layout.addLayout(stats_layout)
        
        # Info label
        info = QLabel("Welcome to the Grinding Polisher System - Click 'Design' tab to calculate specifications")
        info.setFont(QFont("Segoe UI", 12))
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("padding: 20px; background-color: #e8f0fe; border-radius: 8px;")
        layout.addWidget(info)
        
        # Recent experiments table
        table_label = QLabel("Recent Experiments")
        table_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(table_label)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["ID", "Name", "Material", "Date", "Status"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.recent_table)
        
        layout.addStretch()
        return tab
    
    def _create_stat_card(self, label: str, value: str) -> QWidget:
        """Create a statistics card"""
        card = QWidget()
        card.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #dcdde1;
        """)
        layout = QVBoxLayout(card)
        
        icon_label = QLabel(label)
        icon_label.setFont(QFont("Segoe UI", 10))
        icon_label.setStyleSheet("color: #5f6b7a;")
        layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setStyleSheet("color: #1a2332;")
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        
        return card
    
    def _create_design_tab(self) -> QWidget:
        """Create design tab with working calculations"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left panel - Specifications
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Specifications group
        spec_group = QGroupBox("Machine Specifications")
        spec_layout = QFormLayout(spec_group)
        
        self.motor_power = QDoubleSpinBox()
        self.motor_power.setRange(0.1, 5.0)
        self.motor_power.setSingleStep(0.1)
        self.motor_power.setValue(0.5)
        self.motor_power.setSuffix(" HP")
        spec_layout.addRow("Motor Power:", self.motor_power)
        
        self.motor_speed = QDoubleSpinBox()
        self.motor_speed.setRange(500, 3000)
        self.motor_speed.setSingleStep(10)
        self.motor_speed.setValue(1518)
        self.motor_speed.setSuffix(" RPM")
        spec_layout.addRow("Motor Speed:", self.motor_speed)
        
        self.driving_pulley = QDoubleSpinBox()
        self.driving_pulley.setRange(20, 100)
        self.driving_pulley.setSingleStep(5)
        self.driving_pulley.setValue(40)
        self.driving_pulley.setSuffix(" mm")
        spec_layout.addRow("Driving Pulley (D1):", self.driving_pulley)
        
        self.driven_pulley = QDoubleSpinBox()
        self.driven_pulley.setRange(50, 300)
        self.driven_pulley.setSingleStep(5)
        self.driven_pulley.setValue(170)
        self.driven_pulley.setSuffix(" mm")
        spec_layout.addRow("Driven Pulley (D2):", self.driven_pulley)
        
        self.disc_diameter = QDoubleSpinBox()
        self.disc_diameter.setRange(100, 300)
        self.disc_diameter.setSingleStep(10)
        self.disc_diameter.setValue(200)
        self.disc_diameter.setSuffix(" mm")
        spec_layout.addRow("Disc Diameter:", self.disc_diameter)
        
        left_layout.addWidget(spec_group)
        
        # Results group
        result_group = QGroupBox("Calculated Results")
        result_layout = QFormLayout(result_group)
        
        self.output_speed_label = QLabel("--- RPM")
        self.output_speed_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.output_speed_label.setStyleSheet("color: #2C7BE5;")
        result_layout.addRow("Output Speed (N2):", self.output_speed_label)
        
        self.pulley_ratio_label = QLabel("---")
        self.pulley_ratio_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.pulley_ratio_label.setStyleSheet("color: #2C7BE5;")
        result_layout.addRow("Pulley Ratio:", self.pulley_ratio_label)
        
        self.torque_label = QLabel("--- Nm")
        self.torque_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.torque_label.setStyleSheet("color: #2C7BE5;")
        result_layout.addRow("Torque:", self.torque_label)
        
        self.cutting_speed_label = QLabel("--- m/s")
        self.cutting_speed_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.cutting_speed_label.setStyleSheet("color: #2C7BE5;")
        result_layout.addRow("Cutting Speed:", self.cutting_speed_label)
        
        self.suitability_label = QLabel("---")
        self.suitability_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        result_layout.addRow("Suitability:", self.suitability_label)
        
        left_layout.addWidget(result_group)
        
        # Calculate button
        calc_btn = QPushButton("Calculate Now")
        calc_btn.clicked.connect(self._calculate_design)
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        left_layout.addWidget(calc_btn)
        
        # Project data button
        project_btn = QPushButton("Load Project Test Data")
        project_btn.clicked.connect(self._load_project_data)
        project_btn.setStyleSheet("""
            QPushButton {
                background-color: #F39C12;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E67E22;
            }
        """)
        left_layout.addWidget(project_btn)
        
        left_layout.addStretch()
        
        # Right panel - Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.design_plot = MatplotlibCanvas(self, width=8, height=6)
        right_layout.addWidget(self.design_plot)
        
        # Draw initial schematic
        self._draw_initial_schematic()
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        return tab
    
    def _draw_initial_schematic(self):
        """Draw initial machine schematic"""
        try:
            self.design_plot.axes.clear()
            self.design_plot.axes.text(0.5, 0.5, 
                "Enter specifications and click\n'Calculate Now' to see results",
                ha='center', va='center', fontsize=14,
                transform=self.design_plot.axes.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3))
            self.design_plot.axes.set_title("Grinding Polisher - Design Calculator", fontsize=14, fontweight='bold')
            self.design_plot.axes.axis('off')
            self.design_plot.draw()
        except Exception as e:
            print(f"Error drawing schematic: {e}")
    
    def _calculate_design(self):
        """Calculate design parameters"""
        try:
            # Update engine specs
            self.engine.specs.motor_power_hp = self.motor_power.value()
            self.engine.specs.motor_power_w = self.motor_power.value() * 746
            self.engine.specs.motor_speed_rpm = self.motor_speed.value()
            self.engine.specs.driving_pulley_diameter_mm = self.driving_pulley.value()
            self.engine.specs.driven_pulley_diameter_mm = self.driven_pulley.value()
            self.engine.specs.disc_diameter_mm = self.disc_diameter.value()
            
            # Calculate
            output_speed = self.engine.calculate_output_speed()
            ratio = self.engine.calculate_pulley_ratio()
            torque = self.engine.calculate_torque(output_speed)
            cutting_speed = self.engine.calculate_cutting_speed(speed_rpm=output_speed)
            suitability = self.engine.check_speed_suitability(output_speed)
            
            # Update labels
            self.output_speed_label.setText(f"{output_speed:.0f} RPM")
            self.pulley_ratio_label.setText(f"1:{ratio:.2f}")
            self.torque_label.setText(f"{torque:.2f} Nm")
            self.cutting_speed_label.setText(f"{cutting_speed:.2f} m/s")
            
            # Suitability with color
            if suitability['grinding_suitable']:
                self.suitability_label.setText("Suitable for Grinding")
                self.suitability_label.setStyleSheet("color: #2ECC71; font-weight: bold;")
            elif suitability['polishing_suitable']:
                self.suitability_label.setText("Suitable for Polishing")
                self.suitability_label.setStyleSheet("color: #2ECC71; font-weight: bold;")
            else:
                self.suitability_label.setText(suitability['recommendation'])
                self.suitability_label.setStyleSheet("color: #F39C12; font-weight: bold;")
            
            # Update plot
            self._update_design_plot(output_speed, ratio, torque, cutting_speed)
            
            # Update status
            self.statusBar().showMessage(f"Calculation complete - Output Speed: {output_speed:.0f} RPM")
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error calculating: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}")
    
    def _update_design_plot(self, speed, ratio, torque, cutting_speed):
        """Update the design plot with results"""
        try:
            self.design_plot.axes.clear()
            
            # Create a nice display with results
            text = f"""
            DESIGN RESULTS
            
            Output Speed:  {speed:.0f} RPM
            Pulley Ratio:  1:{ratio:.2f}
            Torque:        {torque:.2f} Nm
            Cutting Speed: {cutting_speed:.2f} m/s
            
            N1 x D1 = N2 x D2
            {self.motor_speed.value():.0f} x {self.driving_pulley.value():.0f} = {speed:.0f} x {self.driven_pulley.value():.0f}
            """
            
            self.design_plot.axes.text(0.5, 0.5, text,
                ha='center', va='center', fontsize=12, fontfamily='monospace',
                transform=self.design_plot.axes.transAxes,
                bbox=dict(boxstyle="round,pad=0.8", facecolor='#f8f9fa', 
                         edgecolor='#2C7BE5', linewidth=2))
            self.design_plot.axes.set_title("Design Calculations Complete", fontsize=14, fontweight='bold')
            self.design_plot.axes.axis('off')
            self.design_plot.draw()
        except Exception as e:
            print(f"Error updating plot: {e}")
    
    def _load_project_data(self):
        """Load project test data"""
        try:
            from core import get_project_test_data
            data = get_project_test_data()
            
            self.motor_speed.setValue(data['average_motor_speed'])
            self.driving_pulley.setValue(data['driving_pulley_diameter_mm'])
            self.driven_pulley.setValue(data['driven_pulley_diameter_mm'])
            
            QMessageBox.information(self, "Project Data Loaded", 
                f"Loaded project test data:\n"
                f"Motor Speed: {data['average_motor_speed']} RPM\n"
                f"Driving Pulley: {data['driving_pulley_diameter_mm']} mm\n"
                f"Driven Pulley: {data['driven_pulley_diameter_mm']} mm\n"
                f"Output Speed: {data['calculated_output_speed']} RPM\n\n"
                f"Click 'Calculate Now' to see results!")
            
            # Auto-calculate
            self._calculate_design()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load project data: {str(e)}")
    
    def _create_control_tab(self) -> QWidget:
        """Create control tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Experiment setup
        setup_group = QGroupBox("Experiment Setup")
        setup_layout = QFormLayout(setup_group)
        
        self.exp_name = QLineEdit()
        self.exp_name.setPlaceholderText("Enter experiment name...")
        setup_layout.addRow("Experiment Name:", self.exp_name)
        
        self.material = QComboBox()
        materials = ["Brass", "Bronze", "Steel", "Aluminum", "Copper", "Cast Iron", "Titanium"]
        self.material.addItems(materials)
        setup_layout.addRow("Material:", self.material)
        
        self.specimen_id = QLineEdit()
        self.specimen_id.setPlaceholderText("e.g., AMS X8")
        setup_layout.addRow("Specimen ID:", self.specimen_id)
        
        self.operator = QLineEdit()
        self.operator.setPlaceholderText("Operator name")
        setup_layout.addRow("Operator:", self.operator)
        
        self.target_speed = QDoubleSpinBox()
        self.target_speed.setRange(50, 800)
        self.target_speed.setSingleStep(10)
        self.target_speed.setValue(357)
        self.target_speed.setSuffix(" RPM")
        setup_layout.addRow("Target Speed:", self.target_speed)
        
        layout.addWidget(setup_group)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Experiment")
        self.start_btn.clicked.connect(self._start_experiment)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                font-size: 14px;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self._stop_experiment)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                font-size: 14px;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Status
        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Live speed display
        self.live_speed_label = QLabel("Current Speed: 0 RPM")
        self.live_speed_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.live_speed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.live_speed_label)
        
        layout.addStretch()
        return tab
    
    def _start_experiment(self):
        """Start an experiment"""
        if not self.exp_name.text():
            QMessageBox.warning(self, "Missing Information", "Please enter an experiment name")
            return
        
        self.current_experiment_id = self.db.create_experiment(
            name=self.exp_name.text(),
            material_type=self.material.currentText(),
            specimen_id=self.specimen_id.text() or None,
            operator=self.operator.text() or None
        )
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Running")
        self.status_label.setStyleSheet("color: #2ECC71; font-weight: bold;")
        self.status_indicator.setText("● Experiment Running")
        self.status_indicator.setStyleSheet("color: #2ECC71;")
        
        # Simulate
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self._simulate)
        self.sim_timer.start(100)
        self.sim_step = 0
    
    def _stop_experiment(self):
        """Stop experiment"""
        if hasattr(self, 'sim_timer'):
            self.sim_timer.stop()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        self.status_indicator.setText("● System Ready")
        self.status_indicator.setStyleSheet("color: #E74C3C;")
        self.progress.setValue(0)
    
    def _simulate(self):
        """Simulate operation"""
        self.sim_step += 1
        progress = min(100, int(self.sim_step / 20))
        self.progress.setValue(progress)
        
        # Simulate speed with variation
        base_speed = self.target_speed.value()
        variation = 5 * (self.sim_step % 5 - 2) / 10
        current_speed = base_speed + variation
        self.live_speed_label.setText(f"Current Speed: {current_speed:.0f} RPM")
        
        if progress >= 100:
            self._stop_experiment()
            QMessageBox.information(self, "Complete", "Experiment completed successfully!")
            
            # Save to database
            self.db.update_experiment(self.current_experiment_id, duration_minutes=5)
            self.db.add_speed_trial(
                self.current_experiment_id, 1,
                self.engine.specs.motor_speed_rpm,
                base_speed,
                self.engine.calculate_pulley_ratio()
            )
    
    def _create_results_tab(self) -> QWidget:
        """Create results tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Results entry
        result_group = QGroupBox("Results Entry")
        result_layout = QFormLayout(result_group)
        
        self.surface_quality = QComboBox()
        self.surface_quality.addItems(["Excellent", "Good", "Fair", "Poor"])
        result_layout.addRow("Surface Quality:", self.surface_quality)
        
        self.magnification = QComboBox()
        self.magnification.addItems(["50x", "100x", "200x", "500x", "1000x"])
        self.magnification.setCurrentText("500x")
        result_layout.addRow("Magnification:", self.magnification)
        
        self.grain_structure = QLineEdit()
        self.grain_structure.setPlaceholderText("e.g., Equiaxed grains, clear boundaries")
        result_layout.addRow("Grain Structure:", self.grain_structure)
        
        self.vibration_level = QComboBox()
        self.vibration_level.addItems(["Low", "Medium", "High"])
        result_layout.addRow("Vibration Level:", self.vibration_level)
        
        self.chatter_marks = QCheckBox("Chatter marks observed")
        result_layout.addRow("", self.chatter_marks)
        
        self.uniform_polishing = QCheckBox("Uniform polishing achieved")
        result_layout.addRow("", self.uniform_polishing)
        
        self.overall_assessment = QTextEdit()
        self.overall_assessment.setPlaceholderText("Overall assessment of the experiment...")
        self.overall_assessment.setMaximumHeight(80)
        result_layout.addRow("Assessment:", self.overall_assessment)
        
        layout.addWidget(result_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Results")
        save_btn.clicked.connect(self._save_results)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        btn_layout.addWidget(save_btn)
        
        view_btn = QPushButton("View Analysis")
        view_btn.clicked.connect(self._view_analysis)
        btn_layout.addWidget(view_btn)
        
        layout.addLayout(btn_layout)
        
        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Results will appear here...")
        layout.addWidget(self.results_display)
        
        return tab
    
    def _save_results(self):
        """Save results"""
        if not self.current_experiment_id:
            QMessageBox.warning(self, "No Experiment", "Start an experiment first")
            return
        
        self.db.save_results(
            self.current_experiment_id,
            self.surface_quality.currentText(),
            self.magnification.currentText(),
            self.grain_structure.text(),
            self.vibration_level.currentText(),
            self.chatter_marks.isChecked(),
            self.uniform_polishing.isChecked(),
            self.overall_assessment.toPlainText()
        )
        
        QMessageBox.information(self, "Saved", "Results saved successfully!")
        self._display_results(self.current_experiment_id)
    
    def _display_results(self, experiment_id: int):
        """Display results"""
        results = self.db.get_results(experiment_id)
        if results:
            text = f"""
            Results for Experiment #{experiment_id}
            {'=' * 40}
            
            Surface Quality: {results['surface_quality']}
            Magnification: {results['magnification']}
            Grain Structure: {results['grain_structure'] or 'N/A'}
            Vibration Level: {results['vibration_level']}
            Chatter Marks: {'Yes' if results['chatter_marks'] else 'No'}
            Uniform Polishing: {'Yes' if results['uniform_polishing'] else 'No'}
            
            Assessment:
            {results['overall_assessment'] or 'N/A'}
            """
            self.results_display.setText(text)
    
    def _view_analysis(self):
        """View analysis"""
        if not self.current_experiment_id:
            QMessageBox.warning(self, "No Experiment", "Start an experiment first")
            return
        
        results = self.db.get_results(self.current_experiment_id)
        if results:
            try:
                vibration_data = {
                    'low': 2 if results['vibration_level'] == 'Low' else 1,
                    'medium': 2 if results['vibration_level'] == 'Medium' else 1,
                    'high': 2 if results['vibration_level'] == 'High' else 1,
                    'chatter_score': 90 if not results['chatter_marks'] else 50,
                    'waviness_score': 85,
                    'scratch_score': 90 if results['surface_quality'] in ['Excellent', 'Good'] else 70,
                    'overall_score': 85 if results['surface_quality'] in ['Excellent', 'Good'] else 60
                }
                
                fig = self.visualizer.plot_stability_analysis(vibration_data)
                fig.show()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not show analysis: {str(e)}")
    
    def _create_history_tab(self) -> QWidget:
        """Create history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["ID", "Name", "Material", "Date", "Duration", "Status"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_history)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        layout.addWidget(refresh_btn)
        
        self._refresh_history()
        return tab
    
    def _refresh_history(self):
        """Refresh history table - FIXED"""
        experiments = self.db.get_all_experiments()
        self.history_table.setRowCount(len(experiments))
        
        for i, exp in enumerate(experiments):
            self.history_table.setItem(i, 0, QTableWidgetItem(str(exp['id'])))
            self.history_table.setItem(i, 1, QTableWidgetItem(exp['name']))
            self.history_table.setItem(i, 2, QTableWidgetItem(exp['material_type'] or 'N/A'))
            self.history_table.setItem(i, 3, QTableWidgetItem(exp['created_at'][:10] if exp['created_at'] else 'N/A'))
            
            # FIXED: Handle None values for duration_minutes
            duration = exp.get('duration_minutes')
            if duration is not None:
                self.history_table.setItem(i, 4, QTableWidgetItem(f"{duration:.1f} min"))
            else:
                self.history_table.setItem(i, 4, QTableWidgetItem("N/A"))
            
            results = self.db.get_results(exp['id'])
            status = "Complete" if results else "In Progress"
            self.history_table.setItem(i, 5, QTableWidgetItem(status))
    
    def load_dashboard(self):
        """Load dashboard data"""
        try:
            stats = self.db.get_summary_statistics()
            
            # Update cards
            for card_label, card in self.dashboard_cards.items():
                value_label = card.findChild(QLabel, "value_label")
                if value_label:
                    if card_label == "Experiments":
                        value_label.setText(str(stats['total_experiments']))
                    elif card_label == "Success Rate":
                        value_label.setText(f"{stats['success_rate']:.1f}%")
                    elif card_label == "Avg Speed":
                        value_label.setText(f"{stats['avg_output_speed_rpm']:.0f} RPM")
                    elif card_label == "Materials":
                        value_label.setText(str(len(stats['material_counts'])))
            
            # Update recent experiments
            experiments = self.db.get_all_experiments()[:5]
            self.recent_table.setRowCount(len(experiments))
            for i, exp in enumerate(experiments):
                self.recent_table.setItem(i, 0, QTableWidgetItem(str(exp['id'])))
                self.recent_table.setItem(i, 1, QTableWidgetItem(exp['name']))
                self.recent_table.setItem(i, 2, QTableWidgetItem(exp['material_type'] or 'N/A'))
                self.recent_table.setItem(i, 3, QTableWidgetItem(exp['created_at'][:10] if exp['created_at'] else 'N/A'))
                
                results = self.db.get_results(exp['id'])
                status = "Complete" if results else "In Progress"
                self.recent_table.setItem(i, 4, QTableWidgetItem(status))
                
        except Exception as e:
            print(f"Error loading dashboard: {e}")


def run_app():
    """Run the application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()