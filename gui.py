import os
import time
import json
import pickle
import threading
import subprocess
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

OPTIMIZER_PROCESS = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OptiKey - Keyboard Layout Optimizer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --surface: rgba(30, 41, 59, 0.7);
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --accent: #8b5cf6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --glass-border: rgba(255, 255, 255, 0.1);
            --key-bg: rgba(15, 23, 42, 0.6);
            --key-border: rgba(255, 255, 255, 0.05);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.15), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.15), transparent 25%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            overflow-x: hidden;
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeInDown 0.8s ease-out;
        }

        .header h1 {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }

        .header p {
            color: var(--text-muted);
            font-size: 1.1rem;
        }

        .dashboard {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 2rem;
            width: 100%;
            max-width: 1200px;
        }

        .glass-panel {
            background: var(--surface);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 1.5rem;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            animation: fadeInUp 0.8s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .glass-panel:hover {
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        }

        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .layout-display {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            margin: 2rem 0;
        }

        .keyboard-row {
            display: flex;
            gap: 0.5rem;
        }

        /* Add offset for staggered keyboard look */
        .keyboard-row:nth-child(2) { margin-left: 1.5rem; }
        .keyboard-row:nth-child(3) { margin-left: 3rem; }

        .key {
            width: 3.5rem;
            height: 3.5rem;
            background: var(--key-bg);
            border: 1px solid var(--key-border);
            border-radius: 0.75rem;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
            box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.05), 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .key::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .key:hover {
            transform: translateY(-2px);
            box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.1), 0 6px 12px rgba(0, 0, 0, 0.4);
        }

        .key:hover::before {
            opacity: 1;
        }

        /* Finger colors */
        .finger-0, .finger-7 { color: #fca5a5; } /* Pinky */
        .finger-1, .finger-6 { color: #fde047; } /* Ring */
        .finger-2, .finger-5 { color: #86efac; } /* Middle */
        .finger-3, .finger-4 { color: #93c5fd; } /* Index */

        .score-display {
            text-align: center;
            margin-top: 1rem;
        }

        .score-value {
            font-size: 3rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #10b981;
            text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
            transition: color 0.3s ease;
        }

        .controls {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .btn {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            border: none;
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
            filter: brightness(1.1);
        }

        .btn:active {
            transform: translateY(1px);
        }

        .btn-stop {
            background: linear-gradient(135deg, #ef4444, #b91c1c);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        }

        .btn-stop:hover {
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
        }

        .btn:disabled {
            background: #475569;
            box-shadow: none;
            cursor: not-allowed;
            transform: none;
            filter: none;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #64748b;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
        }

        .status-dot.active {
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 2s infinite;
        }

        .metric-list {
            list-style: none;
            margin-top: 1.5rem;
        }

        .metric-item {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--glass-border);
        }

        .metric-item:last-child {
            border-bottom: none;
        }

        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }

        .logs {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 0.75rem;
            padding: 1rem;
            height: 200px;
            overflow-y: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #cbd5e1;
            margin-top: 1.5rem;
            border: 1px solid var(--glass-border);
        }

        .logs p { margin-bottom: 0.25rem; }
        .log-info { color: #60a5fa; }
        .log-success { color: #34d399; }
        .log-warn { color: #fbbf24; }
        .log-error { color: #f87171; }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }

        @media (max-width: 900px) {
            .dashboard { grid-template-columns: 1fr; }
            .keyboard-row { font-size: 1.2rem; }
            .key { width: 3rem; height: 3rem; }
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>OptiKey</h1>
        <p>AI-Powered Ergonomic Keyboard Layout Optimizer</p>
    </div>

    <div class="dashboard">
        <div class="glass-panel">
            <h2>Current Best Layout</h2>
            
            <div class="layout-display" id="keyboard">
                <!-- Filled by JS -->
                <div class="keyboard-row" id="row1"></div>
                <div class="keyboard-row" id="row2"></div>
                <div class="keyboard-row" id="row3"></div>
            </div>

            <div class="score-display">
                <p style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Fitness Score (Lower is better)</p>
                <div class="score-value" id="current-score">---.------</div>
                <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.5rem;" id="last-updated">Waiting for data...</p>
            </div>
            
            <div class="logs" id="terminal-logs">
                <p class="log-info">> OptiKey GUI Initialized.</p>
                <p class="log-info">> Awaiting optimizer start...</p>
            </div>
        </div>

        <div class="glass-panel controls">
            <h2>Control Panel</h2>
            
            <div class="status-indicator">
                <div class="status-dot" id="status-dot"></div>
                <span id="status-text">Optimizer Stopped</span>
            </div>

            <button class="btn" id="btn-start" onclick="startOptimizer()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                Start Optimization
            </button>

            <button class="btn btn-stop" id="btn-stop" onclick="stopOptimizer()" disabled>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>
                Stop Optimization
            </button>

            <ul class="metric-list">
                <li class="metric-item">
                    <span style="color: var(--text-muted);">Corpus Loaded</span>
                    <span class="metric-value" id="metric-corpus" style="color: #60a5fa;">Yes</span>
                </li>
                <li class="metric-item">
                    <span style="color: var(--text-muted);">Workers</span>
                    <span class="metric-value">10 Parallel SA</span>
                </li>
                <li class="metric-item">
                    <span style="color: var(--text-muted);">Algorithm</span>
                    <span class="metric-value">Simulated Annealing</span>
                </li>
            </ul>
        </div>
    </div>

    <script>
        const FINGER = [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7];
        
        function updateLayout(flatStr, score, timestamp) {
            if(!flatStr || flatStr.length !== 30) return;
            
            for(let row=0; row<3; row++) {
                const rowEl = document.getElementById(`row${row+1}`);
                rowEl.innerHTML = '';
                for(let col=0; col<10; col++) {
                    const pos = row * 10 + col;
                    const char = flatStr[pos];
                    const finger = FINGER[pos];
                    
                    const keyEl = document.createElement('div');
                    keyEl.className = `key finger-${finger}`;
                    keyEl.textContent = char;
                    rowEl.appendChild(keyEl);
                }
            }
            
            document.getElementById('current-score').textContent = score.toFixed(6);
            document.getElementById('last-updated').textContent = "Found at: " + new Date(timestamp).toLocaleTimeString();
        }

        function addLog(msg, type='info') {
            const logs = document.getElementById('terminal-logs');
            const p = document.createElement('p');
            p.className = `log-${type}`;
            p.textContent = `> ${msg}`;
            logs.appendChild(p);
            logs.scrollTop = logs.scrollHeight;
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                
                // Update buttons and status
                const isRunning = data.is_running;
                document.getElementById('status-dot').className = isRunning ? 'status-dot active' : 'status-dot';
                document.getElementById('status-text').textContent = isRunning ? 'Optimization Running...' : 'Optimizer Stopped';
                
                document.getElementById('btn-start').disabled = isRunning;
                document.getElementById('btn-stop').disabled = !isRunning;
                
                if(data.best_layout) {
                    updateLayout(data.best_layout.flat, data.best_layout.score, data.best_layout.timestamp);
                }
                
                // Process new logs
                if(data.logs && data.logs.length > 0) {
                    data.logs.forEach(log => addLog(log, 'success'));
                }
                
            } catch (e) {
                console.error("Failed to fetch status");
            }
        }

        async function startOptimizer() {
            addLog("Starting optimizer...", "info");
            await fetch('/api/start', {method: 'POST'});
            fetchStatus();
        }

        async function stopOptimizer() {
            addLog("Stopping optimizer...", "warn");
            await fetch('/api/stop', {method: 'POST'});
            fetchStatus();
        }

        // Poll every 2 seconds
        setInterval(fetchStatus, 2000);
        fetchStatus();
    </script>
</body>
</html>
"""

# Store logs to send to frontend
log_buffer = []

def run_optimizer():
    global OPTIMIZER_PROCESS
    # Run optimizer with unbuffered output
    OPTIMIZER_PROCESS = subprocess.Popen(
        ['python3', 'main.py', 'optimize', '--resume'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    for line in OPTIMIZER_PROCESS.stdout:
        line = line.strip()
        if "★ NEW GLOBAL BEST" in line or "Resumed" in line or "Optimization complete" in line:
            log_buffer.append(line)
            # keep buffer small
            if len(log_buffer) > 50:
                log_buffer.pop(0)
    
    OPTIMIZER_PROCESS.wait()
    OPTIMIZER_PROCESS = None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    global log_buffer
    best_data = None
    best_path = os.path.join('results', 'best_layout.pkl')
    if os.path.exists(best_path):
        try:
            with open(best_path, 'rb') as f:
                best_data = pickle.load(f)
        except:
            pass

    logs_to_send = list(log_buffer)
    log_buffer.clear()
    
    is_running = OPTIMIZER_PROCESS is not None and OPTIMIZER_PROCESS.poll() is None
    
    return jsonify({
        'is_running': is_running,
        'best_layout': best_data,
        'logs': logs_to_send
    })

@app.route('/api/start', methods=['POST'])
def start():
    global OPTIMIZER_PROCESS
    if OPTIMIZER_PROCESS is None or OPTIMIZER_PROCESS.poll() is not None:
        t = threading.Thread(target=run_optimizer)
        t.daemon = True
        t.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already running'})

@app.route('/api/stop', methods=['POST'])
def stop():
    global OPTIMIZER_PROCESS
    if OPTIMIZER_PROCESS is not None:
        OPTIMIZER_PROCESS.terminate()
        OPTIMIZER_PROCESS = None
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'not running'})

if __name__ == '__main__':
    print("Starting OptiKey Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
