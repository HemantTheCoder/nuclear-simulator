import streamlit as st

def render_annunciator_panel(telemetry):
    """Renders a grid of alarm lights."""
    alerts = {
        "SCRAM": telemetry.get("scram", False),
        "HIGH FLUX": telemetry.get("flux", 0) > 1.1,
        "LOW PRES": telemetry.get("pressure", 150) < 100,
        "HIGH TEMP": telemetry.get("temp", 300) > 600,
        "CORE INTG": telemetry.get("health", 100) < 80,
        "RAD WARN": telemetry.get("flux", 0) > 0.8,
        "PUMP TRIP": telemetry.get("flow_rate", 100) < 50,
        "VOID ALRM": telemetry.get("void_fraction", 0) > 0.4,
        "LOW H2O": telemetry.get("water_level", 5) < 3.0,
        "HI PRESS": telemetry.get("pressure", 0) > 170
    }
    
    if telemetry.get("melted", False):
        st.error("CRITICAL CRITICALITY EVENT: CORE MELTDOWN CONFIRMED")
        st.error(f"RADIATION RELEASE: {telemetry.get('radiation_released', 0):.1f} Sv")
    
    st.markdown("""
    <style>
    .annunciator-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 5px;
        margin-bottom: 10px;
        background: #000;
        padding: 5px;
        border: 2px solid #555;
    }
    .alarm-box {
        background-color: #333;
        color: #555;
        text-align: center;
        padding: 8px;
        font-size: 0.7em;
        font-weight: bold;
        border: 1px solid #444;
        border-radius: 2px;
    }
    .alarm-active {
        background-color: #e74c3c;
        color: #fff;
        animation: blink 1s infinite;
        box-shadow: 0 0 10px #e74c3c;
    }
    @keyframes blink { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)
    
    html = '<div class="annunciator-grid">'
    for label, active in alerts.items():
        cls = "alarm-active" if active else ""
        html += f'<div class="alarm-box {cls}">{label}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_event_log(events, title="LIVE EVENT LOG"):
    """Renders a scrolling event log."""
    with st.container(border=True):
        st.markdown(f"**📜 {title}**")
        display_events = events[-5:] if len(events) > 5 else events
        for e in reversed(display_events):
            st.markdown(f"`T+{e['time']:.0f}s`: {e['event']}")
        if not events:
            st.caption("No recent events.")
