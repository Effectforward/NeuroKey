import { useState, useRef, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
  Zap, Settings, Activity, Terminal, Cpu, Play, BarChart3, Sliders, Info, ShieldAlert, Square, RefreshCw, HelpCircle, X
} from 'lucide-react';
import "./App.css";

const PRESETS: Record<string, string> = {
  QWERTY: "Q W E R T Y U I O P\nA S D F G H J K L ;\nZ X C V B N M , . /",
  DVORAK: "' , . P Y F G C R L\nA O E U I D H T N S\n; Q J K X B M W V Z",
  COLEMAK: "Q W F P G J L U Y ;\nA R S T D H N E I O\nZ X C V B K M , . /"
};

const HELP_TEXT: Record<string, string> = {
  steps: "Total attempts to swap keys. Higher means better results but longer wait times.",
  temp: "Controls 'randomness'. High temp explores many layouts; low temp refines the current best.",
  sfb: "Same-Finger Bigram. Penalizes using the same finger for two consecutive letters (e.g. ED).",
  rolls: "Bonus for comfortable inward motions (Pinky -> Index). Makes typing feel fluid.",
  effort: "Penalizes keys far from the home row. High values force common letters to the center.",
  balance: "Target work distribution between left/right hands. 0.5 is perfect symmetry."
};

function App() {
  const [layout, setLayout] = useState(PRESETS.QWERTY);
  const [optimizing, setOptimizing] = useState(false);
  const [score, setScore] = useState(1.423);
  const [progress, setProgress] = useState(0);
  const [history, setHistory] = useState<{ step: number, score: number }[]>([]);
  const [showPresets, setShowPresets] = useState(false);
  const [showHelp, setShowHelp] = useState<string | null>(null);
  const [engineType, setEngineType] = useState<"CPU" | "GPU">("CPU");
  const [coolingStrategy, setCoolingStrategy] = useState("Exponential");
  const [liveUpdates, setLiveUpdates] = useState(true);
  
  // Engine Parameters
  const [steps, setSteps] = useState(1000000);
  const [tStart, setTStart] = useState(2.0);
  const [tEnd, setTEnd] = useState(0.01);
  
  // Advanced Weights
  const [sfbWeight, setSfbWeight] = useState(10.0);
  const [rollBonus, setRollBonus] = useState(3.5);
  const [outwardPenalty, setOutwardPenalty] = useState(0.5);
  const [effortWeight, setEffortWeight] = useState(1.0);
  const [handBias, setHandBias] = useState(0.5);

  const [logs, setLogs] = useState([
    { time: "16:01:42", msg: "Engine standby...", type: "normal" },
    { time: "16:01:43", msg: "Parallel compute ready", type: "normal" },
  ]);

  useEffect(() => {
    const unlisten = listen("best_layout_found", (event: any) => {
      if (liveUpdates) {
        setLayout(event.payload.layout);
        setScore(event.payload.score);
        setProgress(event.payload.progress * 100);
        setHistory(prev => [...prev, { step: prev.length * 1000, score: event.payload.score }].slice(-50));
      }
    });

    return () => {
      unlisten.then(fn => fn());
    };
  }, [liveUpdates]);

  const addLog = (msg: string, type: "normal" | "highlight" = "normal") => {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setLogs(prev => [...prev, { time, msg, type }].slice(-10));
  };

  const applyPreset = (name: string) => {
    setLayout(PRESETS[name]);
    setScore(name === "QWERTY" ? 1.423 : name === "DVORAK" ? 1.152 : 1.185);
    addLog(`Applied ${name} preset`, "highlight");
    setShowPresets(false);
  };

  async function startOptimization() {
    setOptimizing(true);
    setProgress(0);
    addLog(`Initializing ${engineType} engine...`, "highlight");
    setHistory([{ step: 0, score: score }]);
    
    try {
      const weights = {
        sfb: sfbWeight,
        rollBonus: rollBonus,
        effort: effortWeight,
        handBias: handBias,
        outwardPenalty: outwardPenalty
      };

      const finalLayout: string = await invoke("run_optimization", { 
        steps, 
        tStart: tStart, 
        tEnd: tEnd, 
        coolingStrategy: coolingStrategy,
        weights 
      });
      
      setLayout(finalLayout);
      setProgress(100);
      addLog(`${engineType} Optimization complete.`, "highlight");
    } catch (e) {
      addLog("Execution error: " + e, "normal");
    } finally {
      setOptimizing(false);
    }
  }

  const rows = layout.split('\n').map(row => row.trim().split(/\s+/));

  return (
    <div className="app-container">
      {showHelp && (
        <div className="modal-overlay" onClick={() => setShowHelp(null)}>
          <div className="glass help-modal" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <HelpCircle size={24} color="var(--primary)" />
                <h3 style={{ color: 'white' }}>Parameter Guide</h3>
              </div>
              <X size={20} className="clickable" onClick={() => setShowHelp(null)} />
            </div>
            <p style={{ color: 'var(--text-dim)', lineHeight: '1.6' }}>{HELP_TEXT[showHelp]}</p>
            <button className="btn btn-primary" onClick={() => setShowHelp(null)} style={{ marginTop: '1.5rem', width: '100%' }}>Got it</button>
          </div>
        </div>
      )}

      <main>
        <header>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px' }}>
            <Zap size={40} color="var(--primary)" fill="var(--primary)" />
            <h1 className="logo-text">NEUROKEY</h1>
          </div>
          <p className="subtitle">High-Performance Neural Optimizer</p>
        </header>

        <section className="glass keyboard-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
              <div style={{ background: 'var(--primary-glow)', padding: '10px', borderRadius: '12px' }}>
                <Activity size={24} color="var(--primary)" />
              </div>
              <div>
                <span className="label">System Status</span>
                <h2 style={{ fontSize: '1.2rem' }}>{optimizing ? 'Optimizing...' : 'Engine Ready'}</h2>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span className="label">Ergonomic Score</span>
              <div className="value" style={{ color: 'var(--primary)', fontSize: '2.5rem' }}>{score.toFixed(4)}</div>
            </div>
          </div>

          <div className="keyboard-container">
            {rows.map((row, rowIndex) => (
              <div key={rowIndex} className={`keyboard-row row-${rowIndex}`}>
                {row.map((key, keyIndex) => (
                  <div key={keyIndex} className="key">
                    {key}
                  </div>
                ))}
              </div>
            ))}
          </div>

          <div className="chart-container glass" style={{ padding: '20px', marginTop: '3rem', background: 'rgba(0,0,0,0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1rem' }}>
              <BarChart3 size={18} color="var(--text-dim)" />
              <span className="label">Convergence Graph</span>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: '15px', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                   <RefreshCw size={14} className={optimizing ? "spin" : ""} color="var(--primary)" />
                   <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Live Updates</span>
                   <input type="checkbox" checked={liveUpdates} onChange={() => setLiveUpdates(!liveUpdates)} />
                </div>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={120}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="step" hide />
                <YAxis domain={['auto', 'auto']} hide />
                <Tooltip 
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}
                  itemStyle={{ color: 'var(--primary)' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="var(--primary)" 
                  strokeWidth={2} 
                  dot={false}
                  animationDuration={300}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="btn-group">
            {!optimizing ? (
              <button className="btn btn-primary clickable" onClick={startOptimization} style={{ zIndex: 20 }}>
                <Play size={20} fill="currentColor" />
                Start Engine
              </button>
            ) : (
              <button className="btn btn-primary clickable" onClick={() => {}} style={{ background: '#ff4444', border: 'none', zIndex: 20 }}>
                <Square size={20} fill="currentColor" />
                Running...
              </button>
            )}
            
            <div className="dropdown" style={{ position: 'relative', zIndex: 20 }}>
              <button className="btn btn-outline clickable" onClick={() => setShowPresets(!showPresets)}>
                <Settings size={20} />
                Presets
              </button>
              {showPresets && (
                <div className="glass dropdown-content" style={{ 
                  position: 'absolute', bottom: '100%', left: 0, marginBottom: '10px',
                  width: '180px', display: 'flex', flexDirection: 'column', gap: '5px', padding: '10px',
                  zIndex: 30
                }}>
                  {Object.keys(PRESETS).map(name => (
                    <div 
                      key={name} 
                      className="clickable" 
                      style={{ padding: '8px', borderRadius: '8px', textAlign: 'left', cursor: 'pointer' }}
                      onClick={() => applyPreset(name)}
                    >
                      {name}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>
      </main>

      <aside className="sidebar">
        <div className="glass stat-card config-panel" style={{ maxHeight: '75vh', overflowY: 'auto' }}>
          
          <div style={{ display: 'flex', gap: '10px', marginBottom: '1.5rem' }}>
            <button 
              className={`clickable ${engineType === 'CPU' ? 'active-engine' : ''}`}
              onClick={() => setEngineType('CPU')}
              style={{ flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: engineType === 'CPU' ? 'var(--primary-glow)' : 'transparent', color: 'white', fontSize: '0.8rem' }}
            >
              CPU
            </button>
            <button 
              className={`clickable ${engineType === 'GPU' ? 'active-engine' : ''}`}
              onClick={() => setEngineType('GPU')}
              style={{ flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: engineType === 'GPU' ? 'var(--secondary-glow)' : 'transparent', color: 'white', fontSize: '0.8rem' }}
            >
              GPU
            </button>
          </div>

          <div className="section-title">
            <Sliders size={16} color="var(--primary)" />
            <span>ANNEALING ENGINE</span>
          </div>
          
          <div className="config-item">
            <span className="label" style={{ fontSize: '0.7rem' }}>Cooling Model</span>
            <select value={coolingStrategy} onChange={(e) => setCoolingStrategy(e.target.value)} className="clickable select-input">
              <option>Exponential</option>
              <option>Linear</option>
              <option>Cosine</option>
            </select>
          </div>

          <div className="config-item">
            <div className="config-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '0.8rem' }}>Steps</span>
                <HelpCircle size={12} className="clickable" color="var(--text-dim)" onClick={() => setShowHelp('steps')} />
              </div>
              <span className="config-value">{steps.toLocaleString()}</span>
            </div>
            <input type="range" min="100000" max="10000000" step="100000" value={steps} onChange={(e) => setSteps(Number(e.target.value))} className="clickable" />
          </div>

          <div className="config-item">
            <div className="config-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '0.8rem' }}>Thermal Profile</span>
                <HelpCircle size={12} className="clickable" color="var(--text-dim)" onClick={() => setShowHelp('temp')} />
              </div>
              <span className="config-value">{tStart.toFixed(1)} → {tEnd.toFixed(3)}</span>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input type="range" min="0.5" max="10" step="0.1" value={tStart} onChange={(e) => setTStart(Number(e.target.value))} className="clickable" style={{ flex: 1 }} />
              <input type="range" min="0.001" max="0.1" step="0.001" value={tEnd} onChange={(e) => setTEnd(Number(e.target.value))} className="clickable" style={{ flex: 1 }} />
            </div>
          </div>

          <div className="section-title" style={{ marginTop: '1.5rem' }}>
            <ShieldAlert size={16} color="var(--secondary)" />
            <span>BIOMETRIC WEIGHTS</span>
          </div>

          <div className="config-item">
            <div className="config-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '0.8rem' }}>SFB Penalty</span>
                <HelpCircle size={12} className="clickable" color="var(--text-dim)" onClick={() => setShowHelp('sfb')} />
              </div>
              <span className="config-value secondary">{sfbWeight.toFixed(1)}</span>
            </div>
            <input type="range" min="1" max="50" step="1" value={sfbWeight} onChange={(e) => setSfbWeight(Number(e.target.value))} className="clickable secondary-slider" />
          </div>

          <div className="config-item">
            <div className="config-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '0.8rem' }}>Roll Bonus</span>
                <HelpCircle size={12} className="clickable" color="var(--text-dim)" onClick={() => setShowHelp('rolls')} />
              </div>
              <span className="config-value secondary">{rollBonus.toFixed(1)}</span>
            </div>
            <input type="range" min="0" max="10" step="0.5" value={rollBonus} onChange={(e) => setRollBonus(Number(e.target.value))} className="clickable secondary-slider" />
          </div>

          <div className="config-item">
            <div className="config-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '0.8rem' }}>Effort Weight</span>
                <HelpCircle size={12} className="clickable" color="var(--text-dim)" onClick={() => setShowHelp('effort')} />
              </div>
              <span className="config-value secondary">{effortWeight.toFixed(1)}</span>
            </div>
            <input type="range" min="0.1" max="5" step="0.1" value={effortWeight} onChange={(e) => setEffortWeight(Number(e.target.value))} className="clickable secondary-slider" />
          </div>

          <div className="config-item">
            <div className="config-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ fontSize: '0.8rem' }}>Hand Balance</span>
                <HelpCircle size={12} className="clickable" color="var(--text-dim)" onClick={() => setShowHelp('balance')} />
              </div>
              <span className="config-value secondary">{handBias.toFixed(2)}</span>
            </div>
            <input type="range" min="0" max="1" step="0.05" value={handBias} onChange={(e) => setHandBias(Number(e.target.value))} className="clickable secondary-slider" />
          </div>
        </div>

        <div className="glass stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={16} color="var(--primary)" />
              <span className="label">ENGINE LOAD</span>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--primary)', fontFamily: 'JetBrains Mono' }}>{progress.toFixed(0)}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill fill-primary" style={{ width: `${progress}%` }}></div>
          </div>
        </div>

        <div className="glass stat-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: '150px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
            <Terminal size={16} color="var(--primary)" />
            <span className="label">Engine Telemetry</span>
          </div>
          <div className="log-container">
            {logs.map((log, i) => (
              <div key={i} className={`log-entry ${log.type === 'highlight' ? 'highlight' : ''}`}>
                <span style={{ color: '#444', marginRight: '8px' }}>[{log.time}]</span>
                {log.msg}
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}

export default App;
