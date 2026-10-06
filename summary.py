"""
summary.py - Display experiment summary
"""

from database import Database

def main():
    db = Database()
    stats = db.get_summary_statistics()
    
    print('=' * 50)
    print('EXPERIMENT SUMMARY')
    print('=' * 50)
    print(f'Total Experiments: {stats["total_experiments"]}')
    print(f'Success Rate: {stats["success_rate"]:.1f}%')
    print(f'Average Speed: {stats["avg_output_speed_rpm"]:.0f} RPM')
    print(f'Materials Tested: {len(stats["material_counts"])}')
    print('=' * 50)
    
    for mat, count in stats['material_counts'].items():
        print(f'  {mat}: {count} experiments')
    
    print('=' * 50)
    
    # Show all experiments
    experiments = db.get_all_experiments()
    if experiments:
        print('\nRECENT EXPERIMENTS:')
        print('-' * 50)
        for exp in experiments:
            results = db.get_results(exp['id'])
            status = '✅ Complete' if results else '⏳ In Progress'
            print(f"ID: {exp['id']} | {exp['name']} | {exp['material_type'] or 'N/A'} | {status}")

if __name__ == "__main__":
    main()