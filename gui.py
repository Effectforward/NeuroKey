import os
import time
import json
import pickle
import threading
import subprocess
import signal
import psutil
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            margin-bottom: 2rem;
            animation: fadeInDown 0.8s ease-out;
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }

        .header p {
            color: var(--text-muted);
            font-size: 1rem;
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
            padding: 1.5rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            animation: fadeInUp 0.8s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        h2 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: #e2e8f0;
        }

        .layout-display {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            margin: 1rem 0;
        }

        .keyboard-row {
            display: flex;
            gap: 0.5rem;
        }

        .keyboard-row:nth-child(2) { margin-left: 1.5rem; }
        .keyboard-row:nth-child(3) { margin-left: 3rem; }

        .key {
            width: 3rem;
            height: 3rem;
            background: var(--key-bg);
            border: 1px solid var(--key-border);
            border-radius: 0.75rem;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.25rem;
            font-weight: 700;
            color: #fff;
            box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.05), 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .finger-0, .finger-7 { color: #fca5a5; }
        .finger-1, .finger-6 { color: #fde047; }
        .finger-2, .finger-5 { color: #86efac; }
        .finger-3, .finger-4 { color: #93c5fd; }

        .score-display {
            text-align: center;
            margin-top: 1rem;
        }

        .score-value {
            font-size: 2.5rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #10b981;
            text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
        }

        .controls {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .btn {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            width: 100%;
        }

        .btn:hover { filter: brightness(1.1); transform: translateY(-2px); }
        .btn-stop { background: linear-gradient(135deg, #ef4444, #b91c1c); }
        .btn:disabled { background: #475569; cursor: not-allowed; transform: none; filter: none; }

        .status-indicator {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(0,0,0,0.3);
            padding: 0.75rem;
            border-radius: 0.75rem;
            border: 1px solid var(--glass-border);
        }

        .status-dot {
            width: 12px; height: 12px; border-radius: 50%; background: #64748b;
        }
        .status-dot.active {
            background: #10b981; box-shadow: 0 0 10px #10b981; animation: pulse 2s infinite;
        }

        .settings-form {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        .settings-form label { font-size: 0.85rem; color: var(--text-muted); }
        .settings-form input, .settings-form select {
            width: 100%; padding: 0.5rem; border-radius: 0.5rem; border: 1px solid var(--glass-border);
            background: rgba(0,0,0,0.3); color: white; font-family: 'Inter', sans-serif;
        }

        .logs {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 0.75rem;
            padding: 1rem;
            height: 150px;
            overflow-y: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #cbd5e1;
            margin-top: 1rem;
            border: 1px solid var(--glass-border);
        }
        .log-info { color: #60a5fa; }
        .log-success { color: #34d399; }
        .log-warn { color: #fbbf24; }
        
        .charts {
            margin-top: 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            width: 100%;
            max-width: 1200px;
        }
        .chart-container {
            position: relative;
            height: 200px;
            width: 100%;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>OptiKey Control Center</h1>
        <p>AI-Powered Ergonomic Keyboard Layout Optimizer</p>
    </div>

    <div class="dashboard">
        <div class="glass-panel" style="display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h2>Current Best Layout</h2>
                <div class="layout-display" id="keyboard">
                    <div class="keyboard-row" id="row1"></div>
                    <div class="keyboard-row" id="row2"></div>
                    <div class="keyboard-row" id="row3"></div>
                </div>
                <div class="score-display">
                    <p style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">Fitness Score</p>
                    <div class="score-value" id="current-score">---.------</div>
                </div>
            </div>
            <div class="logs" id="terminal-logs">
                <p class="log-info">> System Initialized.</p>
            </div>
        </div>

        <div class="glass-panel controls">
            <h2>Control Panel</h2>
            <div class="status-indicator">
                <span id="status-text" style="font-weight: 600;">Stopped</span>
                <div class="status-dot" id="status-dot"></div>
            </div>

            <div class="settings-form">
                <div>
                    <label>CPU Workers (Cores)</label>
                    <input type="number" id="cfg-workers" value="10" min="1" max="128">
                </div>
                <div>
                    <label>Cooling Schedule</label>
                    <select id="cfg-cooling">
                        <option value="exponential">Exponential (Default)</option>
                        <option value="linear">Linear</option>
                    </select>
                </div>
                <div>
                    <label>Steps per Run</label>
                    <input type="number" id="cfg-steps" value="50000000">
                </div>
            </div>

            <button class="btn" id="btn-start" onclick="startOptimizer()">Start Optimization</button>
            <button class="btn btn-stop" id="btn-stop" onclick="stopOptimizer()" disabled>Stop Optimization</button>
        </div>
    </div>

    <div class="charts">
        <div class="glass-panel">
            <h2>CPU & RAM Usage</h2>
            <div class="chart-container">
                <canvas id="sysChart"></canvas>
            </div>
        </div>
        <div class="glass-panel">
            <h2>Optimizer Temperature</h2>
            <div class="chart-container" style="display:flex; justify-content:center; align-items:center;">
                <p style="color:var(--text-muted); text-align:center;">Temperature drops as the algorithm fine-tunes the layout. <br/><br/><i>Currently only tracked via console logs.</i></p>
            </div>
        </div>
    </div>

    <script>
        const FINGER = [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7];
        
        // Setup Chart
        const ctx = document.getElementById('sysChart').getContext('2d');
        const sysChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [
                    { label: 'CPU %', borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', data: Array(20).fill(0), fill: true, tension: 0.4 },
                    { label: 'RAM %', borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', data: Array(20).fill(0), fill: true, tension: 0.4 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: false,
                scales: { y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.1)' } }, x: { grid: { display: false } } },
                plugins: { legend: { labels: { color: '#fff' } } }
            }
        });

        function updateLayout(flatStr, score) {
            if(!flatStr || flatStr.length !== 30) return;
            for(let row=0; row<3; row++) {
                const rowEl = document.getElementById(`row${row+1}`);
                rowEl.innerHTML = '';
                for(let col=0; col<10; col++) {
                    const pos = row * 10 + col;
                    const char = flatStr[pos];
                    const keyEl = document.createElement('div');
                    keyEl.className = `key finger-${FINGER[pos]}`;
                    keyEl.textContent = char;
                    rowEl.appendChild(keyEl);
                }
            }
            document.getElementById('current-score').textContent = score.toFixed(6);
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
                
                const isRunning = data.is_running;
                document.getElementById('status-dot').className = isRunning ? 'status-dot active' : 'status-dot';
                document.getElementById('status-text').textContent = isRunning ? 'Running' : 'Stopped';
                
                document.getElementById('btn-start').disabled = isRunning;
                document.getElementById('btn-stop').disabled = !isRunning;
                
                if(data.best_layout) updateLayout(data.best_layout.flat, data.best_layout.score);
                
                if(data.logs && data.logs.length > 0) {
                    data.logs.forEach(log => addLog(log, 'success'));
                }
                
                // Update chart
                sysChart.data.datasets[0].data.shift();
                sysChart.data.datasets[0].data.push(data.system.cpu);
                sysChart.data.datasets[1].data.shift();
                sysChart.data.datasets[1].data.push(data.system.ram);
                sysChart.update();

            } catch (e) {
                console.error("Failed to fetch status");
            }
        }

        async function startOptimizer() {
            const workers = document.getElementById('cfg-workers').value;
            const steps = document.getElementById('cfg-steps').value;
            const cooling = document.getElementById('cfg-cooling').value;
            
            addLog(`Starting with ${workers} workers...`, "info");
            await fetch('/api/start', {
                method: 'POST', 
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({workers, steps, cooling})
            });
            fetchStatus();
        }

        async function stopOptimizer() {
            addLog("Sending SIGTERM to process group...", "warn");
            await fetch('/api/stop', {method: 'POST'});
            fetchStatus();
        }

        setInterval(fetchStatus, 2000);
        fetchStatus();
    </script>
</body>
</html>
"""

log_buffer = []

def run_optimizer(workers, steps, cooling):
    global OPTIMIZER_PROCESS
    cmd = ['python3', 'main.py', 'optimize', '--resume']
    if workers: cmd.extend(['--workers', str(workers)])
    if steps: cmd.extend(['--steps', str(steps)])
    if cooling: cmd.extend(['--cooling', cooling])
    
    # Run optimizer in a new process group so we can kill all children easily
    OPTIMIZER_PROCESS = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        preexec_fn=os.setsid
    )
    for line in OPTIMIZER_PROCESS.stdout:
        line = line.strip()
        if "★ NEW GLOBAL BEST" in line or "Resumed" in line or "OPTIMIZATION COMPLETE" in line:
            log_buffer.append(line)
            if len(log_buffer) > 50: log_buffer.pop(0)
    
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
            with open(best_path, 'rb') as f: best_data = pickle.load(f)
        except: pass

    logs_to_send = list(log_buffer)
    log_buffer.clear()
    
    is_running = OPTIMIZER_PROCESS is not None and OPTIMIZER_PROCESS.poll() is None
    
    sys_stats = {
        'cpu': psutil.cpu_percent(),
        'ram': psutil.virtual_memory().percent
    }
    
    return jsonify({
        'is_running': is_running,
        'best_layout': best_data,
        'logs': logs_to_send,
        'system': sys_stats
    })

@app.route('/api/start', methods=['POST'])
def start():
    global OPTIMIZER_PROCESS
    if OPTIMIZER_PROCESS is None or OPTIMIZER_PROCESS.poll() is not None:
        data = request.json or {}
        w = data.get('workers')
        s = data.get('steps')
        c = data.get('cooling')
        t = threading.Thread(target=run_optimizer, args=(w, s, c))
        t.daemon = True
        t.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already running'})

@app.route('/api/stop', methods=['POST'])
def stop():
    global OPTIMIZER_PROCESS
    if OPTIMIZER_PROCESS is not None:
        # Kill the entire process group
        try:
            os.killpg(os.getpgid(OPTIMIZER_PROCESS.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Error killing process group: {e}")
        OPTIMIZER_PROCESS = None
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'not running'})

if __name__ == '__main__':
    print("Starting OptiKey GUI Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
