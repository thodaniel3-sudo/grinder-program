"""
quick_test.py - Quick system test
"""

from core import GrindingPolisherEngine
from database import Database
from reports import ReportGenerator
from visualization import GrindingPolisherVisualizer

def main():
    print('=' * 50)
    print('QUICK SYSTEM TEST')
    print('=' * 50)
    
    # Test 1: Core Engine
    print('\n[1] Testing Core Engine...')
    engine = GrindingPolisherEngine()
    speed = engine.calculate_output_speed()
    ratio = engine.calculate_pulley_ratio()
    print(f'    Output Speed: {speed:.0f} RPM')
    print(f'    Pulley Ratio: 1:{ratio:.2f}')
    
    # Test 2: Database
    print('\n[2] Testing Database...')
    db = Database()
    stats = db.get_summary_statistics()
    print(f'    Total Experiments: {stats["total_experiments"]}')
    print(f'    Success Rate: {stats["success_rate"]:.1f}%')
    
    # Test 3: Reports
    print('\n[3] Testing Reports...')
    experiments = db.get_all_experiments()
    if experiments:
        rg = ReportGenerator(db)
        try:
            pdf = rg.generate_experiment_report(experiments[0]['id'])
            print(f'    ✅ PDF Report: {pdf}')
        except Exception as e:
            print(f'    ❌ PDF Error: {e}')
    else:
        print('    ⚠️  No experiments found')
    
    # Test 4: Visualization
    print('\n[4] Testing Visualization...')
    vis = GrindingPolisherVisualizer()
    try:
        fig = vis.draw_pulley_diagram()
        print('    ✅ Visualization working')
    except Exception as e:
        print(f'    ❌ Visualization Error: {e}')
    
    print('\n' + '=' * 50)
    print('✅ ALL TESTS COMPLETED')
    print('=' * 50)

if __name__ == "__main__":
    main()