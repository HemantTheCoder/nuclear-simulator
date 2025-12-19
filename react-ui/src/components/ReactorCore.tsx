import React from 'react';

interface ReactorCoreProps {
    temp: number;
    flux: number;
    rods: number;
}

export const ReactorCore: React.FC<ReactorCoreProps> = ({ temp, flux, rods }) => {
    // Color Logic
    let fill = "#3498db"; // Blue
    if (temp > 500) fill = "#ffffff";
    else if (temp > 420) fill = "#e74c3c"; // Red
    else if (temp > 380) fill = "#e67e22"; // Orange
    else if (temp > 320) fill = "#2ecc71"; // Green (Nominal)

    const rodHeight = 20 + (rods / 100.0) * 160;
    const glowOpacity = Math.min(1.0, flux * 0.8);

    return (
        <div style={{ background: '#222', padding: '20px', borderRadius: '10px', textAlign: 'center', border: '1px solid #444' }}>
            <h3 style={{ color: '#ccc', marginBottom: '10px' }}>REACTOR VESSEL</h3>
            <svg width="200" height="300" viewBox="0 0 300 400">
                <defs>
                    <radialGradient id="cerenkov" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                        <stop offset="0%" stopColor="#00ffff" stopOpacity={glowOpacity} />
                        <stop offset="100%" stopColor="#0000ff" stopOpacity="0" />
                    </radialGradient>
                </defs>

                {/* Vessel */}
                <rect x="50" y="20" width="200" height="360" rx="20" ry="20" fill="#2c3e50" stroke="#95a5a6" strokeWidth="4" />

                {/* Core Fuel */}
                <rect x="70" y="100" width="160" height="200" fill={fill} opacity="0.8" rx="5" />
                <rect x="70" y="100" width="160" height="200" fill="url(#cerenkov)" rx="5" />

                {/* Control Rods */}
                <rect x="90" y="20" width="20" height={rodHeight} fill="#7f8c8d" stroke="#bdc3c7" />
                <rect x="140" y="20" width="20" height={rodHeight} fill="#7f8c8d" stroke="#bdc3c7" />
                <rect x="190" y="20" width="20" height={rodHeight} fill="#7f8c8d" stroke="#bdc3c7" />

                {/* Particles */}
                <circle cx="100" cy="300" r="3" fill="rgba(255,255,255,0.5)">
                    <animate attributeName="cy" from="300" to="100" dur={`${Math.max(0.2, 2.0 - flux)}s`} repeatCount="indefinite" />
                </circle>
                <circle cx="150" cy="300" r="4" fill="rgba(255,255,255,0.5)">
                    <animate attributeName="cy" from="320" to="100" dur={`${Math.max(0.3, 2.5 - flux)}s`} repeatCount="indefinite" />
                </circle>
            </svg>
        </div>
    );
};
