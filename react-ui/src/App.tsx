import React, { useState } from 'react';
import './App.css';
import { ControlRoom } from './components/ControlRoom';

function App() {
    const [inSim, setInSim] = useState(false);

    if (!inSim) {
        return (
            <div className="landing">
                <div className="landing-content">
                    <h1 className="nuclear-title">Nuclear Reactor<br />Systems Simulator</h1>
                    <div className="nuclear-subtitle">Understanding control, stability, and safety in complex energy systems.</div>

                    <div className="safety-panel">
                        <div className="safety-header">⚠️ SIMULATION CONTEXT & SAFETY BRIEF</div>
                        <ul>
                            <li><strong>Conceptual Simulator:</strong> Models physics principles, not operational procedures.</li>
                            <li><strong>Safety Focus:</strong> Understand stability margins and failure modes.</li>
                            <li><strong>"You are learning how complex systems behave."</strong></li>
                        </ul>
                    </div>

                    <button className="enter-btn" onClick={() => setInSim(true)}>
                        ENTER CONTROL ROOM ☢️
                    </button>
                </div>
            </div>
        );
    }

    return <ControlRoom />;
}

export default App;
