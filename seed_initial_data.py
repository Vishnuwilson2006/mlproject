"""
seed_initial_data.py
Populates SQLite database with sample prediction records for all 14 electronic circuits.
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'circuit_project.settings')
django.setup()

from surrogate_app.models import PredictionHistory
from surrogate_app.circuit_engine import CIRCUIT_REGISTRY

def seed():
    print("Seeding initial prediction records for all 14 circuits...")
    
    # Clear existing old format records
    PredictionHistory.objects.all().delete()
    
    count = 0
    for slug, config in CIRCUIT_REGISTRY.items():
        # Generate initial sample inputs
        sample_inputs = {}
        for inp in config['inputs']:
            sample_inputs[inp['name']] = inp['default']
            
        # Calculate sample output
        try:
            calc_result = config['calc'](sample_inputs)
            outputs_dict = {out['name']: calc_result.get(out['name'], 0.0) for out in config['outputs']}
            score = calc_result.get('score', 95.0)
            
            PredictionHistory.objects.create(
                circuit_slug=slug,
                circuit_title=config['title'],
                circuit_category=config['category'],
                inputs_json=json.dumps(sample_inputs),
                outputs_json=json.dumps(outputs_dict),
                performance_score=score
            )
            count += 1
        except Exception as e:
            print(f"Error seeding {slug}: {e}")
            
    print(f"Successfully seeded {count} records across all 14 circuits.")

if __name__ == "__main__":
    seed()
