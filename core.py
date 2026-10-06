"""
core.py - Engineering calculations, constants, and validation for the Grinding Polisher

This module contains all the engineering logic, design calculations,
and validation functions for the grinding polisher machine.
"""

import math
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class MaterialType(Enum):
    """Material types for specimen preparation"""
    BRASS = "Brass"
    BRONZE = "Bronze"
    STEEL = "Steel"
    ALUMINUM = "Aluminum"
    COPPER = "Copper"
    CAST_IRON = "Cast Iron"
    STAINLESS_STEEL = "Stainless Steel"
    TITANIUM = "Titanium"


class AbrasiveGrit(Enum):
    """Standard abrasive grit sizes for metallographic preparation"""
    # Grinding grits
    P80 = 80
    P120 = 120
    P180 = 180
    P240 = 240
    P320 = 320
    P400 = 400
    P600 = 600
    P800 = 800
    P1000 = 1000
    P1200 = 1200
    P1500 = 1500
    P2000 = 2000
    P2500 = 2500
    P3000 = 3000
    P4000 = 4000
    
    # Polishing
    DIAMOND_1 = "1 micron diamond"
    DIAMOND_3 = "3 micron diamond"
    DIAMOND_6 = "6 micron diamond"
    DIAMOND_9 = "9 micron diamond"
    ALUMINA_005 = "0.05 micron alumina"
    ALUMINA_01 = "0.1 micron alumina"
    ALUMINA_03 = "0.3 micron alumina"
    SILICA = "Colloidal silica"


@dataclass
class MachineSpecifications:
    """Complete machine design specifications"""
    # Motor specifications
    motor_power_hp: float = 0.5
    motor_power_w: float = 373  # 0.5 HP = 373 W
    motor_speed_rpm: float = 1518  # Measured average
    
    # Pulley system
    driving_pulley_diameter_mm: float = 40.0
    driven_pulley_diameter_mm: float = 170.0
    
    # Disc specifications
    disc_diameter_mm: float = 200.0
    number_of_discs: int = 2
    disc_spacing_mm: float = 100.0
    
    # Machine dimensions (cm)
    top_width_cm: float = 64.0
    top_depth_cm: float = 58.0
    rear_height_cm: float = 27.0
    rear_width_cm: float = 53.0
    rear_depth_cm: float = 26.0
    overall_height_cm: float = 30.0
    
    # Weight (kg)
    estimated_weight_kg: float = 45.0
    
    # Speed ranges
    grinding_speed_min_rpm: float = 300.0
    grinding_speed_max_rpm: float = 600.0
    polishing_speed_min_rpm: float = 100.0
    polishing_speed_max_rpm: float = 300.0


class GrindingPolisherEngine:
    """Core engineering calculations for the grinding polisher"""
    
    def __init__(self, specs: Optional[MachineSpecifications] = None):
        self.specs = specs or MachineSpecifications()
        self._calculated_speed = None
        
    def calculate_output_speed(self, 
                              motor_speed: float = None,
                              d1: float = None,
                              d2: float = None) -> float:
        """
        Calculate output platen speed using pulley ratio
        
        N₁D₁ = N₂D₂ (Pulley speed relationship)
        
        Args:
            motor_speed: Input motor speed in RPM
            d1: Driving pulley diameter in mm
            d2: Driven pulley diameter in mm
            
        Returns:
            Output speed in RPM
        """
        motor_speed = motor_speed or self.specs.motor_speed_rpm
        d1 = d1 or self.specs.driving_pulley_diameter_mm
        d2 = d2 or self.specs.driven_pulley_diameter_mm
        
        if d2 == 0:
            raise ValueError("Driven pulley diameter cannot be zero")
            
        output_speed = (motor_speed * d1) / d2
        self._calculated_speed = output_speed
        return output_speed
    
    def calculate_pulley_ratio(self) -> float:
        """Calculate the pulley reduction ratio"""
        return self.specs.driving_pulley_diameter_mm / self.specs.driven_pulley_diameter_mm
    
    def calculate_torque(self, speed_rpm: float = None) -> float:
        """
        Calculate torque at the platen
        
        T = (P × 9549) / n
        
        where:
            T = Torque (Nm)
            P = Power (kW)
            n = Speed (RPM)
        """
        speed = speed_rpm or self.calculate_output_speed()
        power_kw = self.specs.motor_power_w / 1000
        if speed == 0:
            return 0
        return (power_kw * 9549) / speed
    
    def calculate_cutting_speed(self, disc_diameter_mm: float = None, 
                               speed_rpm: float = None) -> float:
        """
        Calculate cutting speed at disc edge
        
        V = π × D × N / 60
        
        Args:
            disc_diameter_mm: Disc diameter in mm
            speed_rpm: Rotational speed in RPM
            
        Returns:
            Cutting speed in m/s
        """
        diameter = disc_diameter_mm or self.specs.disc_diameter_mm
        speed = speed_rpm or self.calculate_output_speed()
        
        if speed == 0:
            return 0
        
        # Convert diameter to meters
        diameter_m = diameter / 1000
        # V = π × D × N (RPS) = π × D × N_RPM / 60
        return (math.pi * diameter_m * speed) / 60
    
    def check_speed_suitability(self, speed_rpm: float) -> Dict[str, any]:
        """Check if speed is suitable for grinding/polishing"""
        grinding_suitable = (self.specs.grinding_speed_min_rpm <= speed_rpm <= 
                           self.specs.grinding_speed_max_rpm)
        polishing_suitable = (self.specs.polishing_speed_min_rpm <= speed_rpm <= 
                            self.specs.polishing_speed_max_rpm)
        
        return {
            'speed': speed_rpm,
            'grinding_suitable': grinding_suitable,
            'polishing_suitable': polishing_suitable,
            'recommendation': self._get_speed_recommendation(speed_rpm)
        }
    
    def _get_speed_recommendation(self, speed_rpm: float) -> str:
        """Get recommendation for given speed"""
        if speed_rpm < self.specs.polishing_speed_min_rpm:
            return "Speed too low for effective material removal"
        elif speed_rpm <= self.specs.polishing_speed_max_rpm:
            return "Suitable for polishing operations"
        elif speed_rpm <= self.specs.grinding_speed_min_rpm:
            return "Transition zone - use with caution"
        elif speed_rpm <= self.specs.grinding_speed_max_rpm:
            return "Suitable for grinding operations"
        else:
            return "Speed too high - risk of thermal damage"
    
    def calculate_grinding_pressure(self, applied_force_n: float, 
                                  area_mm2: float) -> float:
        """
        Calculate grinding pressure
        
        P = F / A
        
        Args:
            applied_force_n: Applied force in Newtons
            area_mm2: Contact area in mm²
            
        Returns:
            Pressure in MPa
        """
        if area_mm2 == 0:
            return 0
        return (applied_force_n * 1000) / area_mm2  # Convert N/mm² to MPa
    
    def estimate_material_removal_rate(self, speed_rpm: float, 
                                      pressure_mpa: float,
                                      grit_size: float) -> float:
        """
        Estimate material removal rate (simplified model)
        
        MRR ∝ V × P × (1/√grit)
        
        Args:
            speed_rpm: Platen speed
            pressure_mpa: Grinding pressure
            grit_size: Grit size in μm (for diamond) or ANSI number
            
        Returns:
            Estimated MRR in mm³/min (relative value)
        """
        # Convert speed to m/s
        v = self.calculate_cutting_speed(speed_rpm=speed_rpm)
        
        # For standard grits (P numbers), estimate size
        if grit_size > 1000:  # Large number = fine grit
            grit_um = 10000 / grit_size  # Approximate conversion
        else:
            grit_um = grit_size
            
        if grit_um == 0:
            return 0
            
        # Simplified MRR model
        return v * pressure_mpa / math.sqrt(grit_um) * 0.01
    
    def get_full_specification(self) -> Dict[str, any]:
        """Get all machine specifications with calculated values"""
        output_speed = self.calculate_output_speed()
        torque = self.calculate_torque(output_speed)
        cutting_speed = self.calculate_cutting_speed(speed_rpm=output_speed)
        
        return {
            'specifications': {
                'motor_power_hp': self.specs.motor_power_hp,
                'motor_power_w': self.specs.motor_power_w,
                'motor_speed_rpm': self.specs.motor_speed_rpm,
                'driving_pulley_diameter_mm': self.specs.driving_pulley_diameter_mm,
                'driven_pulley_diameter_mm': self.specs.driven_pulley_diameter_mm,
                'disc_diameter_mm': self.specs.disc_diameter_mm,
                'pulley_ratio': self.calculate_pulley_ratio(),
            },
            'calculated': {
                'output_speed_rpm': output_speed,
                'torque_nm': torque,
                'cutting_speed_m_s': cutting_speed,
                'speed_suitability': self.check_speed_suitability(output_speed)
            }
        }
    
    def validate_design(self) -> List[str]:
        """Validate design parameters and return list of issues"""
        issues = []
        specs = self.specs
        
        # Check motor power
        if specs.motor_power_hp < 0.25:
            issues.append("Motor power may be insufficient for grinding operations")
        
        # Check speed suitability
        speed = self.calculate_output_speed()
        if speed < specs.grinding_speed_min_rpm:
            issues.append(f"Output speed ({speed:.0f} RPM) is below recommended grinding speed range")
        
        # Check pulley ratio
        ratio = self.calculate_pulley_ratio()
        if ratio < 2 or ratio > 6:
            issues.append(f"Pulley ratio ({ratio:.2f}) may not be optimal - consider redesign")
        
        # Check disc diameter
        if specs.disc_diameter_mm < 150 or specs.disc_diameter_mm > 300:
            issues.append(f"Disc diameter ({specs.disc_diameter_mm}mm) may not be optimal")
        
        return issues


# ===================== PRESET DATA =====================

# Standard abrasive sequences for different materials
ABRASIVE_SEQUENCES = {
    'brass': {
        'material': MaterialType.BRASS,
        'grinding': [
            AbrasiveGrit.P240,
            AbrasiveGrit.P400,
            AbrasiveGrit.P600,
            AbrasiveGrit.P800,
            AbrasiveGrit.P1000,
        ],
        'polishing': [
            AbrasiveGrit.DIAMOND_6,
            AbrasiveGrit.DIAMOND_3,
            AbrasiveGrit.DIAMOND_1,
            AbrasiveGrit.ALUMINA_005,
        ]
    },
    'bronze': {
        'material': MaterialType.BRONZE,
        'grinding': [
            AbrasiveGrit.P240,
            AbrasiveGrit.P400,
            AbrasiveGrit.P600,
            AbrasiveGrit.P800,
            AbrasiveGrit.P1000,
        ],
        'polishing': [
            AbrasiveGrit.DIAMOND_6,
            AbrasiveGrit.DIAMOND_3,
            AbrasiveGrit.DIAMOND_1,
            AbrasiveGrit.ALUMINA_005,
        ]
    },
    'steel': {
        'material': MaterialType.STEEL,
        'grinding': [
            AbrasiveGrit.P180,
            AbrasiveGrit.P320,
            AbrasiveGrit.P600,
            AbrasiveGrit.P800,
            AbrasiveGrit.P1200,
        ],
        'polishing': [
            AbrasiveGrit.DIAMOND_6,
            AbrasiveGrit.DIAMOND_3,
            AbrasiveGrit.DIAMOND_1,
        ]
    },
    'aluminum': {
        'material': MaterialType.ALUMINUM,
        'grinding': [
            AbrasiveGrit.P320,
            AbrasiveGrit.P600,
            AbrasiveGrit.P800,
            AbrasiveGrit.P1200,
            AbrasiveGrit.P2000,
        ],
        'polishing': [
            AbrasiveGrit.DIAMOND_3,
            AbrasiveGrit.DIAMOND_1,
            AbrasiveGrit.SILICA,
        ]
    }
}

# Recommended speeds for different processes
RECOMMENDED_SPEEDS = {
    'rough_grinding': {'min': 400, 'max': 600, 'default': 500},
    'fine_grinding': {'min': 300, 'max': 450, 'default': 380},
    'rough_polishing': {'min': 200, 'max': 300, 'default': 250},
    'fine_polishing': {'min': 100, 'max': 200, 'default': 150},
}

# Coolant recommendations
COOLANT_RECOMMENDATIONS = {
    'brass': 'Water-based coolant with corrosion inhibitor',
    'bronze': 'Water-based coolant with corrosion inhibitor',
    'steel': 'Soluble oil emulsion (5-10%)',
    'aluminum': 'Kerosene or specialized aluminum coolant',
    'copper': 'Water-based coolant with corrosion inhibitor',
    'cast_iron': 'Soluble oil emulsion (5-10%)',
}


# ===================== TEST DATA (From Project) =====================

def get_project_test_data():
    """Return the test data from the project report"""
    return {
        'trial_1': {'motor_speed': 1566},
        'trial_2': {'motor_speed': 1487},
        'trial_3': {'motor_speed': 1502},
        'average_motor_speed': 1518,
        'driving_pulley_diameter_mm': 40,
        'driven_pulley_diameter_mm': 170,
        'calculated_output_speed': 357,
        'measured_output_speed': 357,
        'specimen': 'AMS X8 (Brass/Bronze alloy)',
        'magnification': '500x',
        'surface_quality': 'Highly reflective, planarized, equiaxed grains visible',
        'stability': 'Minor run-out at pulley, no catastrophic chatter'
    }