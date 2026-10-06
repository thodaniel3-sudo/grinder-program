"""
visualization.py - Charts, graphs, and engineering diagrams

This module provides visualization functions for the grinding polisher
application including speed plots, engineering diagrams, and performance charts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import numpy as np
from typing import Dict, List, Tuple, Optional
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Try to import plotly for interactive plots
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class GrindingPolisherVisualizer:
    """Visualization tools for the grinding polisher"""
    
    def __init__(self):
        self.figsize = (10, 6)
        self.dpi = 100
    
    # ===================== ENGINEERING DIAGRAMS =====================
    
    def draw_machine_schematic(self, ax=None, show_dimensions: bool = True) -> plt.Figure:
        """
        Draw a schematic diagram of the grinding polisher machine
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))
        else:
            fig = ax.figure
        
        # Machine dimensions (scaled for visualization)
        width = 10
        height = 6
        base_y = 0
        
        # Main body - rear housing
        rear_rect = Rectangle((0, base_y + 2), 4, 3, 
                             facecolor='lightgray', edgecolor='black', 
                             linewidth=2, alpha=0.8, label='Rear Housing')
        ax.add_patch(rear_rect)
        
        # Top working surface
        top_rect = Rectangle((0, base_y + 5), 10, 0.5,
                            facecolor='gray', edgecolor='black',
                            linewidth=2, alpha=0.6, label='Working Surface')
        ax.add_patch(top_rect)
        
        # Discs (2 positions)
        disc_positions = [(2, base_y + 4.2), (7, base_y + 4.2)]
        for i, (x, y) in enumerate(disc_positions):
            disc = Circle((x, y), 1.2, 
                         facecolor='#D4A574', edgecolor='black',
                         linewidth=2, alpha=0.8, 
                         label=f'Hardwood Platen {i+1}')
            ax.add_patch(disc)
            
            # Center shaft
            shaft = Circle((x, y), 0.15, 
                          facecolor='black', edgecolor='black')
            ax.add_patch(shaft)
        
        # Motor (rear)
        motor_rect = Rectangle((4.5, base_y + 1.5), 2, 1.5,
                              facecolor='#4A90D9', edgecolor='black',
                              linewidth=2, alpha=0.8, label='Motor')
        ax.add_patch(motor_rect)
        
        # Pulley and belt (simplified)
        pulley1 = Circle((5.5, base_y + 3.5), 0.5,
                        facecolor='#D4A574', edgecolor='black',
                        linewidth=2)
        ax.add_patch(pulley1)
        
        pulley2 = Circle((2, base_y + 4.2), 0.8,
                        facecolor='#D4A574', edgecolor='black',
                        linewidth=2)
        ax.add_patch(pulley2)
        
        # Belt (simplified)
        belt_x = [5.5, 2]
        belt_y = [3.5, 4.2]
        ax.plot(belt_x, belt_y, 'k--', linewidth=2, label='V-belt')
        
        # Dimensions
        if show_dimensions:
            # Width dimension
            ax.annotate('64 cm', xy=(5, base_y + 4.5), ha='center', 
                       fontsize=10, fontweight='bold')
            ax.plot([0, 10], [base_y + 4.5, base_y + 4.5], 'b-', linewidth=1)
            ax.plot([0, 0], [base_y + 4.4, base_y + 4.6], 'b-')
            ax.plot([10, 10], [base_y + 4.4, base_y + 4.6], 'b-')
            
            # Height dimension
            ax.annotate('30 cm', xy=(-0.8, base_y + 3.5), ha='center',
                       fontsize=10, fontweight='bold', rotation=90)
            ax.plot([-0.5, -0.5], [base_y, base_y + 5], 'b-', linewidth=1)
            ax.plot([-0.6, -0.4], [base_y, base_y], 'b-')
            ax.plot([-0.6, -0.4], [base_y + 5, base_y + 5], 'b-')
            
            # Disc spacing
            ax.annotate('100 mm', xy=(4.5, base_y + 3.5), ha='center',
                       fontsize=9, fontweight='bold')
            ax.plot([2, 7], [base_y + 3.2, base_y + 3.2], 'b-', linewidth=1)
            
            # Disc diameter
            ax.annotate('Φ200 mm', xy=(7, base_y + 5.5), ha='center',
                       fontsize=9, fontweight='bold')
        
        # Labels and formatting
        ax.set_xlim(-2, 12)
        ax.set_ylim(base_y - 0.5, 7)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Grinding Polisher - Engineering Schematic', 
                    fontsize=14, fontweight='bold')
        
        # Legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), 
                 loc='upper right', fontsize=9)
        
        return fig
    
    def draw_pulley_diagram(self, ax=None, d1: float = 40, d2: float = 170) -> plt.Figure:
        """
        Draw the pulley system diagram showing speed reduction
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        else:
            fig = ax.figure
        
        # Scale for visualization
        scale = 0.5
        r1 = (d1 / 2) * scale
        r2 = (d2 / 2) * scale
        
        # Pulley centers
        center1 = (1, 3)
        center2 = (6, 3)
        
        # Draw pulleys
        pulley1 = Circle(center1, r1, facecolor='#4A90D9', edgecolor='black', 
                        linewidth=2, alpha=0.7, label=f'Driving: {d1}mm')
        ax.add_patch(pulley1)
        
        pulley2 = Circle(center2, r2, facecolor='#E74C3C', edgecolor='black',
                        linewidth=2, alpha=0.7, label=f'Driven: {d2}mm')
        ax.add_patch(pulley2)
        
        # Belt
        belt_top_y = 3 - max(r1, r2)
        belt_bottom_y = 3 + max(r1, r2)
        belt_x = [center1[0], center2[0]]
        
        ax.plot(belt_x, [belt_top_y, belt_top_y], 'k-', linewidth=3, label='Belt')
        ax.plot(belt_x, [belt_bottom_y, belt_bottom_y], 'k-', linewidth=3)
        
        # Center shafts
        ax.plot(center1[0], center1[1], 'ko', markersize=8)
        ax.plot(center2[0], center2[1], 'ko', markersize=8)
        
        # Arrows showing rotation
        self._add_rotation_arrow(ax, center1, r1, 'CCW')
        self._add_rotation_arrow(ax, center2, r2, 'CW')
        
        # Speed labels
        ax.text(center1[0], center1[1] - r1 - 0.5, '1518 RPM', 
               ha='center', fontsize=11, fontweight='bold', color='#2C3E50')
        ax.text(center2[0], center2[1] - r2 - 0.5, '357 RPM',
               ha='center', fontsize=11, fontweight='bold', color='#2C3E50')
        
        # Ratio label
        ratio = d2 / d1
        mid_x = (center1[0] + center2[0]) / 2
        ax.text(mid_x, -0.3, f'Ratio: 1:{ratio:.2f}\nReduction: {ratio:.1f}x',
               ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Set limits
        ax.set_xlim(0, 7.5)
        ax.set_ylim(-1, 5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Pulley System - Speed Reduction', fontsize=14, fontweight='bold')
        
        ax.legend(loc='lower right')
        
        return fig
    
    def _add_rotation_arrow(self, ax, center, radius, direction):
        """Add a rotation arrow around a pulley"""
        theta = np.linspace(0, np.pi/2, 20)
        if direction == 'CCW':
            theta = theta[::-1]
        arrow_radius = radius * 1.1
        x = center[0] + arrow_radius * np.cos(theta + np.pi/4)
        y = center[1] + arrow_radius * np.sin(theta + np.pi/4)
        ax.plot(x, y, 'r-', linewidth=2)
        # Arrowhead
        ax.arrow(x[-2], y[-2], x[-1]-x[-2], y[-1]-y[-2],
                head_width=0.15, head_length=0.15, fc='red', ec='red')
    
    # ===================== PERFORMANCE CHARTS =====================
    
    def plot_speed_comparison(self, motor_speeds: List[float], 
                             output_speeds: List[float],
                             title: str = "Speed Performance") -> plt.Figure:
        """
        Plot motor and output speed comparison
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Bar chart
        trials = list(range(1, len(motor_speeds) + 1))
        width = 0.35
        x = np.arange(len(trials))
        
        ax1.bar(x - width/2, motor_speeds, width, label='Motor Speed', color='#4A90D9')
        ax1.bar(x + width/2, output_speeds, width, label='Output Speed', color='#E74C3C')
        ax1.set_xlabel('Trial Number')
        ax1.set_ylabel('Speed (RPM)')
        ax1.set_title('Speed Comparison by Trial')
        ax1.set_xticks(x)
        ax1.set_xticklabels(trials)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Line chart with average
        ax2.plot(trials, motor_speeds, 'o-', label='Motor Speed', color='#4A90D9', linewidth=2)
        ax2.plot(trials, output_speeds, 's-', label='Output Speed', color='#E74C3C', linewidth=2)
        ax2.axhline(y=np.mean(motor_speeds), color='#4A90D9', linestyle='--', 
                   alpha=0.5, label=f'Avg Motor: {np.mean(motor_speeds):.0f} RPM')
        ax2.axhline(y=np.mean(output_speeds), color='#E74C3C', linestyle='--',
                   alpha=0.5, label=f'Avg Output: {np.mean(output_speeds):.0f} RPM')
        ax2.set_xlabel('Trial Number')
        ax2.set_ylabel('Speed (RPM)')
        ax2.set_title('Speed Trends')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_speed_suitability(self, speed_rpm: float,
                               grinding_range: Tuple[float, float] = (300, 600),
                               polishing_range: Tuple[float, float] = (100, 300)) -> plt.Figure:
        """
        Plot speed suitability visualization
        """
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Create bands
        y_pos = 1
        
        # Polishing band
        ax.axhspan(polishing_range[0], polishing_range[1], 
                  ymin=0.1, ymax=0.9, color='green', alpha=0.3, label='Polishing Range')
        
        # Grinding band
        ax.axhspan(grinding_range[0], grinding_range[1],
                  ymin=0.1, ymax=0.9, color='orange', alpha=0.3, label='Grinding Range')
        
        # Current speed
        ax.plot([speed_rpm, speed_rpm], [0, 2], 'r-', linewidth=3, label=f'Current: {speed_rpm:.0f} RPM')
        
        # Add markers for min/max
        ax.plot([grinding_range[0], grinding_range[0]], [0, 2], 'k:', linewidth=1, alpha=0.5)
        ax.plot([grinding_range[1], grinding_range[1]], [0, 2], 'k:', linewidth=1, alpha=0.5)
        ax.plot([polishing_range[0], polishing_range[0]], [0, 2], 'k:', linewidth=1, alpha=0.5)
        ax.plot([polishing_range[1], polishing_range[1]], [0, 2], 'k:', linewidth=1, alpha=0.5)
        
        # Labels
        ax.set_xlabel('Speed (RPM)')
        ax.set_ylabel('Operation Type')
        ax.set_yticks([])
        ax.set_title('Speed Suitability Analysis', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.2)
        ax.set_xlim(0, max(grinding_range[1] + 100, speed_rpm + 100))
        
        # Add text annotations
        ax.text(grinding_range[0] + 10, 1.5, 'Polishing', fontsize=10, alpha=0.7)
        ax.text(grinding_range[0] + 10, 0.5, 'Grinding', fontsize=10, alpha=0.7)
        
        return fig
    
    def plot_abrasive_sequence(self, steps: List[Dict]) -> plt.Figure:
        """
        Plot the abrasive sequence as a Gantt-like chart
        """
        fig, ax = plt.subplots(figsize=(10, 5))
        
        y_pos = np.arange(len(steps))
        
        # Colors for grinding vs polishing
        colors = ['#4A90D9' if step['step_type'] == 'grinding' else '#E74C3C' 
                 for step in steps]
        
        # Create horizontal bars
        durations = [step.get('duration_seconds', 30) for step in steps]
        labels = [f"{step['abrasive_type']} {step['grit_size']}" for step in steps]
        
        ax.barh(y_pos, durations, color=colors, alpha=0.7, edgecolor='black')
        
        # Add labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Duration (seconds)')
        ax.set_title('Abrasive Sequence', fontsize=14, fontweight='bold')
        
        # Add step numbers
        for i, duration in enumerate(durations):
            ax.text(duration + 2, i, f'Step {i+1}', va='center', fontsize=9)
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#4A90D9', alpha=0.7, label='Grinding'),
            Patch(facecolor='#E74C3C', alpha=0.7, label='Polishing')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        return fig
    
    def plot_stability_analysis(self, vibration_data: Dict) -> plt.Figure:
        """
        Plot stability analysis results
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # 1. Vibration level
        levels = ['Low', 'Medium', 'High']
        values = [
            vibration_data.get('low', 0),
            vibration_data.get('medium', 0),
            vibration_data.get('high', 0)
        ]
        axes[0, 0].bar(levels, values, color=['green', 'orange', 'red'])
        axes[0, 0].set_title('Vibration Distribution')
        axes[0, 0].set_ylabel('Occurrences')
        
        # 2. Run-out analysis (simulated)
        angles = np.linspace(0, 2*np.pi, 36)
        runout = [0.02 * np.sin(a) + 0.01 * np.sin(2*a) for a in angles]
        axes[0, 1].plot(angles, runout, 'b-')
        axes[0, 1].set_title('Shaft Run-out Profile')
        axes[0, 1].set_xlabel('Angle (rad)')
        axes[0, 1].set_ylabel('Run-out (mm)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Surface quality meter
        quality_scores = ['Chatter', 'Waviness', 'Scratches', 'Overall']
        scores = [
            vibration_data.get('chatter_score', 80),
            vibration_data.get('waviness_score', 85),
            vibration_data.get('scratch_score', 90),
            vibration_data.get('overall_score', 85)
        ]
        colors = ['#E74C3C' if s < 60 else '#F39C12' if s < 80 else '#2ECC71' for s in scores]
        axes[1, 0].bar(quality_scores, scores, color=colors)
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].set_title('Surface Quality Scores')
        axes[1, 0].set_ylabel('Score (%)')
        axes[1, 0].axhline(y=70, color='orange', linestyle='--', alpha=0.5)
        axes[1, 0].axhline(y=80, color='green', linestyle='--', alpha=0.5)
        
        # 4. Summary gauge
        overall = vibration_data.get('overall_score', 85)
        self._draw_gauge(axes[1, 1], overall, 'Overall Stability')
        
        plt.suptitle('Machine Stability Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def _draw_gauge(self, ax, value, label, max_value=100):
        """Draw a simple gauge meter"""
        # Create a half circle
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = np.cos(theta)
        y = np.sin(theta)
        
        # Draw arc
        ax.plot(x, y, 'k-', linewidth=2)
        
        # Fill based on value
        angle = np.pi * value / max_value
        fill_theta = np.linspace(0, angle, 50)
        fill_x = np.cos(fill_theta)
        fill_y = np.sin(fill_theta)
        ax.fill_between(fill_x, 0, fill_y, color='green' if value > 70 else 'orange' if value > 50 else 'red', alpha=0.6)
        
        # Needle
        ax.arrow(0, 0, np.cos(angle)*0.7, np.sin(angle)*0.7,
                head_width=0.1, head_length=0.1, fc='black', ec='black')
        
        # Value display
        ax.text(0, -0.2, f'{value:.0f}%', ha='center', fontsize=14, fontweight='bold')
        ax.text(0, -0.4, label, ha='center', fontsize=10)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
    
    # ===================== 3D PLOTS (if plotly available) =====================
    
    def create_3d_machine_view(self) -> Optional[go.Figure]:
        """Create a 3D interactive view of the machine using plotly"""
        if not PLOTLY_AVAILABLE:
            return None
        
        fig = go.Figure()
        
        # Machine body (simplified as box)
        # This would be expanded for a real 3D visualization
        fig.add_trace(go.Mesh3d(
            x=[0, 10, 10, 0, 0, 10, 10, 0],
            y=[0, 0, 6, 6, 0, 0, 6, 6],
            z=[0, 0, 0, 0, 5, 5, 5, 5],
            i=[0, 0, 0, 4, 4, 4],
            j=[1, 1, 2, 5, 5, 6],
            k=[4, 2, 5, 6, 7, 7],
            opacity=0.3,
            color='lightgray'
        ))
        
        fig.update_layout(
            title='3D Machine View',
            scene=dict(
                xaxis_title='Width',
                yaxis_title='Depth',
                zaxis_title='Height'
            )
        )
        
        return fig
    
    # ===================== REPORT FIGURES =====================
    
    def create_report_figures(self, experiment_data: Dict) -> Dict[str, plt.Figure]:
        """Create all figures for a report"""
        figures = {}
        
        # Speed data
        speed_trials = experiment_data.get('speed_trials', [])
        if speed_trials:
            motor_speeds = [t['motor_speed_rpm'] for t in speed_trials]
            output_speeds = [t['output_speed_rpm'] for t in speed_trials]
            figures['speed_comparison'] = self.plot_speed_comparison(
                motor_speeds, output_speeds
            )
        
        # Machine schematic
        figures['machine_schematic'] = self.draw_machine_schematic()
        
        # Pulley diagram
        figures['pulley_diagram'] = self.draw_pulley_diagram()
        
        # Speed suitability
        if speed_trials:
            avg_output = np.mean([t['output_speed_rpm'] for t in speed_trials])
            figures['speed_suitability'] = self.plot_speed_suitability(avg_output)
        
        return figures