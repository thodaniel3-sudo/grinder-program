"""
generate_reports.py - Generate reports for all experiments
"""

from database import Database
from reports import ReportGenerator
from pathlib import Path

def main():
    db = Database()
    rg = ReportGenerator(db)
    
    experiments = db.get_all_experiments()
    
    if not experiments:
        print('⚠️  No experiments found. Run an experiment first!')
        return
    
    print('=' * 50)
    print('GENERATING REPORTS')
    print('=' * 50)
    
    for exp in experiments:
        exp_id = exp['id']
        exp_name = exp['name']
        
        try:
            # Generate PDF
            pdf_path = rg.generate_experiment_report(exp_id)
            print(f'✅ PDF: {Path(pdf_path).name}')
        except Exception as e:
            print(f'❌ PDF Error for Experiment {exp_id}: {e}')
        
        try:
            # Generate Excel
            excel_path = rg.generate_excel_report(exp_id)
            print(f'✅ Excel: {Path(excel_path).name}')
        except Exception as e:
            print(f'❌ Excel Error for Experiment {exp_id}: {e}')
        
        print('-' * 30)
    
    print('\n📁 Reports saved in: reports/')

if __name__ == "__main__":
    main()