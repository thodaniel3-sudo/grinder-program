"""
reports.py - PDF and Excel report generation for the Grinding Polisher
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import utils

from database import Database


class ReportGenerator:
    """Generate professional PDF and Excel reports"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7F8C8D'),
            fontName='Courier'
        ))
    
    def generate_experiment_report(self, experiment_id: int, 
                                   output_path: str = None) -> str:
        """Generate a PDF report for an experiment"""
        # Get data
        data = self.db.export_experiment_data(experiment_id)
        if not data or not data.get('experiment'):
            raise ValueError(f"No data found for experiment {experiment_id}")
        
        # Create output path
        if output_path is None:
            output_dir = Path(__file__).parent / 'reports'
            output_dir.mkdir(exist_ok=True)
            exp_name = data['experiment']['name'].replace(' ', '_')
            output_path = output_dir / f"Report_{exp_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            f"Grinding Polisher - Experiment Report",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 12))
        
        # Experiment details
        story.append(Paragraph("Experiment Details", self.styles['CustomHeading']))
        story.append(self._create_info_table(data['experiment']))
        story.append(Spacer(1, 12))
        
        # Speed trials
        if data.get('speed_trials'):
            story.append(Paragraph("Speed Trials", self.styles['CustomHeading']))
            story.append(self._create_speed_table(data['speed_trials']))
            story.append(Spacer(1, 12))
            
            # Speed chart
            story.append(self._create_speed_chart(data['speed_trials']))
            story.append(Spacer(1, 12))
        
        # Abrasive sequence
        if data.get('abrasive_sequence'):
            story.append(Paragraph("Abrasive Sequence", self.styles['CustomHeading']))
            story.append(self._create_abrasive_table(data['abrasive_sequence']))
            story.append(Spacer(1, 12))
        
        # Results
        if data.get('results'):
            story.append(Paragraph("Results", self.styles['CustomHeading']))
            story.append(self._create_results_table(data['results']))
            story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 24))
        story.append(Paragraph(
            f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['CustomCode']
        ))
        
        # Build PDF
        doc.build(story)
        
        return str(output_path)
    
    def _create_info_table(self, experiment: Dict) -> Table:
        """Create experiment info table"""
        data = [
            ['Field', 'Value'],
            ['Experiment ID', str(experiment.get('id', 'N/A'))],
            ['Name', experiment.get('name', 'N/A')],
            ['Material Type', experiment.get('material_type', 'N/A')],
            ['Specimen ID', experiment.get('specimen_id', 'N/A')],
            ['Date', experiment.get('date', 'N/A')],
            ['Duration (min)', str(experiment.get('duration_minutes', 'N/A'))],
            ['Operator', experiment.get('operator', 'N/A')],
            ['Notes', experiment.get('notes', 'N/A')],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ECF0F1')),
        ]))
        
        return table
    
    def _create_speed_table(self, speed_trials: List[Dict]) -> Table:
        """Create speed trials table"""
        data = [['Trial', 'Motor Speed (RPM)', 'Output Speed (RPM)', 'Pulley Ratio']]
        
        for trial in speed_trials:
            data.append([
                str(trial.get('trial_number', 'N/A')),
                f"{trial.get('motor_speed_rpm', 0):.0f}",
                f"{trial.get('output_speed_rpm', 0):.0f}",
                f"{trial.get('pulley_ratio', 0):.2f}"
            ])
        
        # Add average row
        if speed_trials:
            avg_motor = sum(t.get('motor_speed_rpm', 0) for t in speed_trials) / len(speed_trials)
            avg_output = sum(t.get('output_speed_rpm', 0) for t in speed_trials) / len(speed_trials)
            data.append([
                'AVERAGE',
                f"{avg_motor:.0f}",
                f"{avg_output:.0f}",
                f"{avg_output/avg_motor:.2f}" if avg_motor > 0 else 'N/A'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD'),
        ]))
        
        return table
    
    def _create_speed_chart(self, speed_trials: List[Dict]) -> Drawing:
        """Create a speed chart"""
        drawing = Drawing(400, 200)
        
        # Prepare data
        trials = list(range(1, len(speed_trials) + 1))
        motor_speeds = [t.get('motor_speed_rpm', 0) for t in speed_trials]
        output_speeds = [t.get('output_speed_rpm', 0) for t in speed_trials]
        
        # Create bar chart
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.width = 300
        bc.height = 120
        bc.data = [motor_speeds, output_speeds]
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(max(motor_speeds), max(output_speeds)) * 1.2
        bc.categoryAxis.categoryNames = [str(t) for t in trials]
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 0
        bc.bars[0].fillColor = colors.HexColor('#4A90D9')
        bc.bars[1].fillColor = colors.HexColor('#E74C3C')
        
        # Legend
        from reportlab.graphics.widgets.legend import Legend
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 350
        legend.y = 150
        legend.colorNamePairs = [
            (colors.HexColor('#4A90D9'), 'Motor Speed'),
            (colors.HexColor('#E74C3C'), 'Output Speed')
        ]
        
        drawing.add(bc)
        drawing.add(legend)
        
        return drawing
    
    def _create_abrasive_table(self, sequence: List[Dict]) -> Table:
        """Create abrasive sequence table"""
        data = [['Step', 'Type', 'Abrasive', 'Grit', 'Duration (s)', 'Pressure (MPa)']]
        
        for step in sequence:
            data.append([
                str(step.get('step_number', 'N/A')),
                step.get('step_type', 'N/A').title(),
                step.get('abrasive_type', 'N/A'),
                step.get('grit_size', 'N/A'),
                str(step.get('duration_seconds', 'N/A')),
                f"{step.get('pressure_mpa', 0):.2f}" if step.get('pressure_mpa') else 'N/A'
            ])
        
        table = Table(data, colWidths=[0.8*inch, 1.2*inch, 1.5*inch, 1.5*inch, 1.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ]))
        
        return table
    
    def _create_results_table(self, results: Dict) -> Table:
        """Create results table"""
        data = [
            ['Parameter', 'Value'],
            ['Surface Quality', results.get('surface_quality', 'N/A')],
            ['Magnification', results.get('magnification', 'N/A')],
            ['Grain Structure', results.get('grain_structure', 'N/A')],
            ['Vibration Level', results.get('vibration_level', 'N/A')],
            ['Chatter Marks', 'Yes' if results.get('chatter_marks') else 'No'],
            ['Uniform Polishing', 'Yes' if results.get('uniform_polishing') else 'No'],
            ['Overall Assessment', results.get('overall_assessment', 'N/A')],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ECF0F1')),
        ]))
        
        return table
    
    def generate_excel_report(self, experiment_id: int, 
                              output_path: str = None) -> str:
        """Generate an Excel report for an experiment"""
        # Get data
        data = self.db.export_experiment_data(experiment_id)
        if not data or not data.get('experiment'):
            raise ValueError(f"No data found for experiment {experiment_id}")
        
        # Create output path
        if output_path is None:
            output_dir = Path(__file__).parent / 'reports'
            output_dir.mkdir(exist_ok=True)
            exp_name = data['experiment']['name'].replace(' ', '_')
            output_path = output_dir / f"Report_{exp_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        # Create Excel file
        with pd.ExcelWriter(str(output_path), engine='openpyxl') as writer:
            # Experiment details
            exp_df = pd.DataFrame([data['experiment']])
            exp_df.to_excel(writer, sheet_name='Experiment Details', index=False)
            
            # Speed trials
            if data.get('speed_trials'):
                speed_df = pd.DataFrame(data['speed_trials'])
                speed_df.to_excel(writer, sheet_name='Speed Trials', index=False)
            
            # Abrasive sequence
            if data.get('abrasive_sequence'):
                seq_df = pd.DataFrame(data['abrasive_sequence'])
                seq_df.to_excel(writer, sheet_name='Abrasive Sequence', index=False)
            
            # Results
            if data.get('results'):
                results_df = pd.DataFrame([data['results']])
                results_df.to_excel(writer, sheet_name='Results', index=False)
        
        return str(output_path)
    
    def export_summary_results(self, technique_results: Dict[str, Dict]) -> str:
        """Export summary results to CSV"""
        try:
            rows = []
            for technique, results in technique_results.items():
                for param, data in results.items():
                    rows.append({
                        'Technique': technique,
                        'Parameter': param,
                        'Value': data.get('value', 'N/A'),
                        'Unit': data.get('unit', ''),
                        'Status': data.get('status', '')
                    })
            
            df = pd.DataFrame(rows)
            
            output_dir = Path(__file__).parent / 'reports'
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"Summary_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            df.to_csv(str(output_path), index=False)
            return str(output_path)
            
        except Exception as e:
            raise ValueError(f"Error exporting summary results: {str(e)}")