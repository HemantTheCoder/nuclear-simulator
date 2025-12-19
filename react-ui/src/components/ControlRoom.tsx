import React, { useState, useEffect, useRef } from 'react';
import { ReactorUnit } from '../logic/ReactorEngine';
import { ReactorCore } from './ReactorCore';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const ControlRoom = () => {
    // Single Unit for now
    const unitRef = useRef(new ReactorUnit("A", "UNIT-1 (PWR)"));
    const [telemetry, setTelemetry] = useState(unitRef.current.telemetry);
    const [controls, setControls] = useState(unitRef.current.controls);
    const [history, setHistory] = useState<any[]>([]);
    const [simTime, setSimTime] = useState(0);

    // Simulation Loop (100ms tick for smooth react)
    useEffect(() => {
        const interval = setInterval(() => {
            unitRef.current.tick(0.1); // 0.1s dt
            setTelemetry({ ...unitRef.current.telemetry });
            setHistory([...unitRef.current.history]);
            setSimTime(unitRef.current.time);
            setControls({ ...unitRef.current.controls }); // Update manual scram reset
        }, 100);
        return () => clearInterval(interval);
    }, []);

    const updateControl = (key: string, val: any) => {
        const u = unitRef.current;
        (u.controls as any)[key] = val;
        setControls({ ...u.controls });
    };

    return (
        <div className="control-room">
            <header className="cr-header">
                <div>
                    <h2>☢️ NUCLEAR CONTROL ROOM</h2>
                    <div className="unit-badge">UNIT-1 (PWR) | STATUS: {telemetry.scram ? "SCRAMMED" : "KC"}</div>
                </div>
                <div className="metrics-bar">
                    <div className="metric">TIME: {simTime.toFixed(1)}s</div>
                    <div className="metric" style={{ color: telemetry.flux > 1.1 ? 'red' : 'inherit' }}>
                        PWR: {telemetry.power_mw.toFixed(1)} MW
                    </div>
                    {telemetry.alerts.length > 0 &&
                        <div className="alert-banner">{telemetry.alerts.join(" | ")}</div>
                    }
                </div>
            </header>

            <div className="cr-grid">
                {/* LEFT: CONTROLS */}
                <div className="panel controls-panel">
                    <h3>🎛 SYSTEM CONTROLS</h3>

                    <button
                        className="scram-btn"
                        onClick={() => updateControl('manual_scram', true)}
                    >
                        🛑 MANUAL SCRAM
                    </button>

                    <div className="control-group">
                        <label>Reactivity (Control Rods) {controls.rods_pos.toFixed(1)}%</label>
                        <input
                            type="range" min="0" max="100" step="0.1"
                            value={controls.rods_pos}
                            onChange={(e) => updateControl('rods_pos', parseFloat(e.target.value))}
                        />
                    </div>

                    <div className="control-group">
                        <label>Primary Coolant Pump {controls.pump_speed.toFixed(0)}%</label>
                        <input
                            type="range" min="0" max="100"
                            value={controls.pump_speed}
                            onChange={(e) => updateControl('pump_speed', parseFloat(e.target.value))}
                        />
                    </div>

                    <div className="control-group">
                        <label>Heat Exchanger Eff {controls.cooling_eff.toFixed(0)}%</label>
                        <input
                            type="range" min="0" max="100"
                            value={controls.cooling_eff}
                            onChange={(e) => updateControl('cooling_eff', parseFloat(e.target.value))}
                        />
                    </div>

                    <div className="control-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={controls.safety_enabled}
                                onChange={(e) => updateControl('safety_enabled', e.target.checked)}
                            /> Safety Interlocks
                        </label>
                    </div>
                </div>

                {/* CENTER: CORE */}
                <div className="panel core-panel">
                    <ReactorCore
                        temp={telemetry.temp}
                        flux={telemetry.flux}
                        rods={controls.rods_pos}
                    />
                </div>

                {/* RIGHT: TELEMETRY */}
                <div className="panel metrics-panel">
                    <h3>📊 SENSORS</h3>
                    <div className="metric-box">
                        <div className="label">Thermal Power</div>
                        <div className="value">{telemetry.power_mw.toFixed(1)} MW</div>
                    </div>
                    <div className="metric-box">
                        <div className="label">Core Temp</div>
                        <div className="value" style={{ color: telemetry.temp > 400 ? 'orange' : 'inherit' }}>
                            {telemetry.temp.toFixed(1)} °C
                        </div>
                    </div>
                    <div className="metric-box">
                        <div className="label">Reactivity</div>
                        <div className="value">{(telemetry.reactivity * 100000).toFixed(1)} pcm</div>
                    </div>
                    <div className="metric-box">
                        <div className="label">Neutron Flux</div>
                        <div className="value">{(telemetry.flux * 100).toFixed(1)} %</div>
                    </div>

                    <div className="chart-container" style={{ height: '200px', marginTop: '20px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={history}>
                                <XAxis dataKey="time" hide />
                                <YAxis domain={['auto', 'auto']} hide />
                                <Tooltip labelStyle={{ color: 'black' }} />
                                <Line type="monotone" dataKey="power" stroke="#8884d8" dot={false} />
                                <Line type="monotone" dataKey="temp" stroke="#82ca9d" dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};
