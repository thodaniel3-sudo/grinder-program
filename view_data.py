"""
view_data.py - View all experiment data
"""

from database import Database

def main():
    db = Database()
    
    experiments = db.get_all_experiments()
    
    if not experiments:
        print('⚠️  No experiments found.')
        return
    
    print('=' * 60)
    print('EXPERIMENT DATA')
    print('=' * 60)
    
    for exp in experiments:
        exp_id = exp['id']
        print(f"\n📊 Experiment #{exp_id}: {exp['name']}")
        print(f"   Material: {exp['material_type'] or 'N/A'}")
        print(f"   Specimen: {exp['specimen_id'] or 'N/A'}")
        print(f"   Date: {exp['created_at'][:10] if exp['created_at'] else 'N/A'}")
        print(f"   Duration: {exp.get('duration_minutes', 'N/A')} min")
        print(f"   Operator: {exp['operator'] or 'N/A'}")
        
        # Get speed trials
        trials = db.get_speed_trials(exp_id)
        if trials:
            print(f"   Speed Trials: {len(trials)}")
            for trial in trials:
                print(f"      Trial {trial['trial_number']}: Motor={trial['motor_speed_rpm']:.0f} RPM, Output={trial['output_speed_rpm']:.0f} RPM")
        
        # Get results
        results = db.get_results(exp_id)
        if results:
            print(f"   Results:")
            print(f"      Surface Quality: {results['surface_quality']}")
            print(f"      Magnification: {results['magnification']}")
            print(f"      Grain Structure: {results['grain_structure'] or 'N/A'}")
            print(f"      Vibration Level: {results['vibration_level']}")
            print(f"      Chatter Marks: {'Yes' if results['chatter_marks'] else 'No'}")
            print(f"      Uniform Polishing: {'Yes' if results['uniform_polishing'] else 'No'}")
        
        print('-' * 60)

if __name__ == "__main__":
    main()