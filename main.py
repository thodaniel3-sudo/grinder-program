"""
main.py - Entry point for the Grinding Polisher Application

This is the main application launcher that initializes everything
and starts the graphical user interface.
"""

import sys
import os
from pathlib import Path

# Add the current directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'PyQt5',
        'matplotlib',
        'pandas',
        'numpy',
        'reportlab',
        'openpyxl',
        'sqlalchemy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("=" * 60)
        print("⚠️  Missing Dependencies Detected!")
        print("=" * 60)
        print("\nThe following packages are required but not installed:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install them using:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        for pkg in missing:
            print(f"  pip install {pkg}")
        print("=" * 60)
        return False
    
    return True


def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'data',
        'reports',
        'logs'
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True)
            print(f"✅ Created directory: {directory}")


def show_splash_screen():
    """Display a splash screen message"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🔬 GRINDING POLISHER - Metallographic System 🔬         ║
    ║                                                              ║
    ║     Fabrication and Development of Grinding Polisher        ║
    ║     Federal University of Technology, Minna                 ║
    ║                                                              ║
    ║     Version: 1.0.0                                          ║
    ║     Date: September, 2026                                   ║
    ║                                                              ║
    ║     Loading...                                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


def run_application():
    """Run the main application"""
    from ui import run_app
    run_app()


def run_console_mode():
    """
    Run in console mode for testing/headless operation
    This is useful for running calculations without the GUI
    """
    print("\n🔧 Running in Console Mode...")
    print("-" * 40)
    
    from core import GrindingPolisherEngine, get_project_test_data
    
    # Initialize engine
    engine = GrindingPolisherEngine()
    
    # Get project test data
    test_data = get_project_test_data()
    
    print("\n📊 Project Test Data:")
    print(f"  Motor Speed (avg): {test_data['average_motor_speed']} RPM")
    print(f"  Driving Pulley: {test_data['driving_pulley_diameter_mm']} mm")
    print(f"  Driven Pulley: {test_data['driven_pulley_diameter_mm']} mm")
    print(f"  Output Speed: {test_data['calculated_output_speed']} RPM")
    
    # Calculate specifications
    print("\n📐 Machine Specifications:")
    spec = engine.get_full_specification()
    for key, value in spec['specifications'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n📈 Calculated Results:")
    for key, value in spec['calculated'].items():
        if isinstance(value, dict):
            print(f"  {key.replace('_', ' ').title()}:")
            for k, v in value.items():
                print(f"    - {k}: {v}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value:.2f}" if isinstance(value, float) else f"  {key.replace('_', ' ').title()}: {value}")
    
    # Validate design
    issues = engine.validate_design()
    if issues:
        print("\n⚠️ Design Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Design validation passed!")
    
    print("\n" + "-" * 40)
    print("Ready to run GUI with: python main.py --gui")


def main():
    """Main entry point"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Grinding Polisher Application')
    parser.add_argument('--gui', action='store_true', help='Launch GUI application')
    parser.add_argument('--console', action='store_true', help='Run in console mode')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    args = parser.parse_args()
    
    # Show splash screen
    show_splash_screen()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Handle command line arguments
    if args.check:
        print("\n✅ All dependencies are installed.")
        sys.exit(0)
    
    if args.console:
        run_console_mode()
        sys.exit(0)
    
    # Default: Run GUI
    # If --gui is specified or no arguments, run GUI
    if args.gui or len(sys.argv) == 1:
        try:
            print("\n🚀 Launching GUI Application...")
            print("   (Close the application window to exit)\n")
            run_application()
        except KeyboardInterrupt:
            print("\n\n👋 Application terminated by user")
        except Exception as e:
            print(f"\n❌ Error running application: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # If other arguments, show help
        parser.print_help()


if __name__ == "__main__":
    main()