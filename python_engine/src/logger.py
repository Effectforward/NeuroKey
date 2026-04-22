import json
import os
from datetime import datetime

PERF_LOG_PATH = os.path.join('results', 'performance_log.json')

def log_performance(engine: str, evals_per_sec: float, best_score: float):
    """
    Log performance metrics for either CPU or GPU engine.
    This maintains a running average or latest reading for the UI chart.
    """
    os.makedirs('results', exist_ok=True)
    
    data = {'cpu_evals_per_sec': 0, 'gpu_evals_per_sec': 0, 'history': []}
    if os.path.exists(PERF_LOG_PATH):
        try:
            with open(PERF_LOG_PATH, 'r') as f:
                data = json.load(f)
        except Exception:
            pass
            
    if engine == 'cpu':
        data['cpu_evals_per_sec'] = evals_per_sec
    elif engine == 'gpu':
        data['gpu_evals_per_sec'] = evals_per_sec
        
    entry = {
        'timestamp': datetime.now().isoformat(),
        'engine': engine,
        'evals_per_sec': evals_per_sec,
        'best_score': best_score
    }
    data['history'].append(entry)
    
    # Keep history from growing forever
    if len(data['history']) > 100:
        data['history'] = data['history'][-100:]
        
    with open(PERF_LOG_PATH, 'w') as f:
        json.dump(data, f)
