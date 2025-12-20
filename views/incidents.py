import streamlit as st
import pandas as pd
import plotly.express as px
import time
from logic.scenarios.historical import SCENARIOS
from logic.engine import ReactorUnit, ReactorType
from services.reporting import ReportGenerator
from logic.visuals import VisualGenerator
from views.components.audio import render_audio_engine
from views.components.ui import render_annunciator_panel, render_event_log
import base64

def show_live_reconstruction(scenario, navigate_func):
    if not scenario:
        st.session_state.mode = None
        st.rerun()
        return
    st.markdown(f"## 🎞️ LIVE RECONSTRUCTION: {scenario.title}")
    
    # Initialize Replay State
    if "replay_unit" not in st.session_state or st.session_state.get("current_replay_id") != scenario.id:
        # Determine base reactor type from scenario info
        r_type = ReactorType.RBMK if "RBMK" in scenario.details[0] else \
                 ReactorType.PWR if "PWR" in scenario.details[0] else \
                 ReactorType.BWR
        
        unit = ReactorUnit("REPLAY", scenario.title, r_type)
        unit.replay_scenario = scenario
        unit.is_replay = True
        unit.time_seconds = 0
        st.session_state.replay_unit = unit
        st.session_state.current_replay_id = scenario.id
        st.session_state.replay_running = True
        st.session_state.replay_debug = "Initialized"

    unit = st.session_state.get("replay_unit")
    if not unit:
        st.error("Replay unit not found in session state.")
        if st.button("Fix & Restart"):
            st.session_state.mode = None
            st.rerun()
        return
    
    with st.sidebar:
        st.markdown("### 📽️ REPLAY CONTROLS")
        st.info(f"Scenario: {scenario.title}")
        
        # --- CONTROLS ---
        if st.button("▶ PLAY" if not st.session_state.replay_running else "⏸ PAUSE", use_container_width=True):
            st.session_state.replay_running = not st.session_state.replay_running
            
        if st.button("🔄 RESTART", use_container_width=True):
            unit.time_seconds = 0
            unit.event_log = []
            st.rerun()

        if st.button("🛑 STOP REPLAY", use_container_width=True):
            st.session_state.selected_incident = None
            st.session_state.replay_unit = None
            st.session_state.mode = None
            st.rerun()

        st.markdown("---")
        if st.button("⚡ TAKE CONTROL", type="primary", use_container_width=True):
            # Hand over this unit to the main simulator
            unit.is_replay = False
            # Break the engine's global scenario bond so it doesn't try to override Unit A
            st.session_state.engine.active_scenario = None 
            st.session_state.engine.units["A"] = unit
            st.session_state.selected_container = "A"
            navigate_func("simulator")
            st.rerun()
            
        st.markdown("---")
        sound_enabled = st.checkbox("🔊 Enable Replay Audio", value=True)

    # --- DASHBOARD (MIRROR SIMULATOR STYLE) ---

    # --- DASHBOARD (MIRROR SIMULATOR STYLE) ---
    col_vis, col_data = st.columns([1.5, 1.2])
    
    with col_vis:
        st.markdown(f"### 🎞️ RECONSTRUCTION: {scenario.title}")
        
        # Annunciator
        render_annunciator_panel(unit.telemetry)
        
        # Audio
        render_audio_engine(unit.telemetry, sound_enabled)
        
        # Historical Phase Indicator (Theatric)
        curr_phase = scenario.phases[0]
        for p in scenario.phases:
            if p['time'] <= unit.time_seconds:
                curr_phase = p
        
        st.markdown(f"""
        <div style="background: rgba(255, 165, 0, 0.1); border-left: 5px solid #ffa500; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h4 style="margin:0; color: #ffa500;">🕵️ HISTORICAL CONTEXT: {curr_phase['label']}</h4>
            <p style="margin: 5px 0; font-size: 0.95em;">{curr_phase['desc']}</p>
            <small style="color: #888;">Timestamp: T+{curr_phase['time']}s | Analysis: {curr_phase.get('analysis', 'Forensic data pending')}</small>
        </div>
        """, unsafe_allow_html=True)

        # SVG Visual
        r_type_str = unit.type.name if hasattr(unit.type, 'name') else str(unit.type).split('.')[-1]
        svg = VisualGenerator.get_reactor_svg({
            "type": r_type_str,
            "temp": unit.telemetry["temp"],
            "flux": unit.telemetry.get("flux", 0.5),
            "rods_pos": unit.telemetry.get("rods", 50),
            "void_fraction": unit.telemetry.get("void_fraction", 0.0),
            "scram": unit.telemetry.get("scram", False),
            "melted": unit.telemetry.get("melted", False)
        })
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{b64_svg}" style="width:100%; max-height:400px;"></div>', unsafe_allow_html=True)

    with col_data:
        st.markdown(f"### 📊 TELEMETRY (T+{unit.time_seconds:.1f}s)")
        
        # Logic Event Log
        render_event_log(unit.event_log, title="RECONSTRUCTION LOG")
        
        # Metrics
        m1, m2 = st.columns(2)
        m1.metric("Power", f"{unit.telemetry['power_mw']:.1f} MW")
        m2.metric("Temp", f"{unit.telemetry['temp']:.1f} °C")
        
        m3, m4 = st.columns(2)
        m3.metric("Pressure", f"{unit.telemetry.get('pressure', 0):.1f} Bar")
        m4.metric("Health", f"{unit.telemetry['health']:.1f}%")
        
        # Graphs
        if unit.history:
            try:
                st.markdown("---")
                df = pd.DataFrame(unit.history)
                # Ensure columns exist before plotting
                plot_cols = [c for c in ["power_mw", "temp"] if c in df.columns]
                x_col = "time_seconds" if "time_seconds" in df.columns else df.columns[0]
                fig = px.line(df, x=x_col, y=plot_cols, title="Parameter Trends")
                fig.update_layout(template="plotly_dark", height=250, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Graph Error: {str(e)}")

    st.markdown("---")

    # --- SIMULATION LOOP ---
    if st.session_state.get("replay_running", False):
        # Scale tick for smoothness (0.1s real-time step)
        unit.tick(0.1)
        time.sleep(0.1) 
        st.rerun()

def show_reconstruction(scenario, navigate_func):
    """Deep-dive static UI (Legacy/Forensic view)."""
    st.markdown(f"## 🕵️ FORENSIC RECONSTRUCTION: {scenario.title}")
    
    if st.button("🚀 START LIVE RE-SIMULATION", type="primary", use_container_width=True):
        st.session_state.mode = "live_replay"
        st.rerun()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📋 INCIDENT DATA")
        for detail in scenario.details:
            st.markdown(f"- {detail}")
            
        st.markdown("---")
        st.markdown("### 📉 HISTORICAL PHASES")
        for phase in scenario.phases:
            with st.expander(f"T+{phase['time']}s: {phase['label']}"):
                st.write(phase['desc'])
                st.caption(f"Analysis: {phase['analysis']}")

    with col2:
        st.markdown("### 📊 TELEMETRY TRENDS")
        history = []
        for phase in scenario.phases:
            d = phase['telemetry'].copy()
            d['time_seconds'] = phase['time']
            history.append(d)
        
        df = pd.DataFrame(history)
        fig = px.line(df, x="time_seconds", y=["power_mw", "temp"], title="Historical Event Sequence")
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### ☢️ FINAL CONSEQUENCES")
        last_phase = scenario.phases[-1]
        t = last_phase['telemetry']
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Peak Temp", f"{t.get('temp', 0):.1f}°C")
        m2.metric("Rad Release", f"{t.get('radiation_released', 0):.2f} Sv")
        m3.metric("Status", "MELTDOWN" if t.get('melted') else "STABLE")
        
        st.markdown("---")
        # Forensic Report Generator
        class MockConfig:
             def __init__(self):
                 self.nominal_power_mw = 3200 if "Chernobyl" in scenario.title else 1000
                 self.nominal_temp = 300
                 self.fuel_limit_temp = 2800

        mock_unit = type('Mock', (), {
            'name': scenario.title,
            'type': type('Type', (), {'name': scenario.id.upper()}),
            'config': MockConfig(),
            'telemetry': t,
            'event_log': [{"timestamp": p['time'], "message": f"{p['label']}: {p['desc']}"} for p in scenario.phases],
            'post_mortem_report': {
                'explanation': scenario.phases[-1]['analysis'],
                'prevention': ["Better design", "Training", "Independent safety"]
            },
            'history': history
        })()
        
        pdf_data = ReportGenerator.generate_pdf(mock_unit, history)
        st.download_button(
            label="📥 DOWNLOAD HISTORICAL FORENSIC REPORT (PDF)",
            data=pdf_data,
            file_name=f"HIS_REPORT_{scenario.id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.button("⬅ BACK TO LIBRARY"):
        st.session_state.selected_incident = None
        st.session_state.mode = None
        st.rerun()

def show(navigate_func):
    """Main Incident Library View."""
    if "selected_incident" not in st.session_state:
        st.session_state.selected_incident = None
    if "mode" not in st.session_state:
        st.session_state.mode = None
        
    if st.session_state.mode == "live_replay":
        show_live_reconstruction(st.session_state.selected_incident, navigate_func)
        return

    if st.session_state.selected_incident:
        show_reconstruction(st.session_state.selected_incident, navigate_func)
        return

    st.markdown("## 🏛 HISTORICAL INCIDENT LIBRARY")
    st.markdown("Select a major event for forensic analysis or LIVE re-simulation.")
    
    st.info("Experience history in real-time or analyze the failure cascade with 20/20 hindsight.")
    
    st.markdown("---")
    for key, sc in SCENARIOS.items():
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                st.title("☢️" if key == "chernobyl" else "⚠️" if key=="tmi" else "🌊")
            with c2:
                st.markdown(f"### {sc.title}")
                st.write(sc.description)
                if st.button(f"ANALYZE CASE: {sc.id.upper()}", key=f"btn_{key}"):
                    st.session_state.selected_incident = sc
                    st.rerun()
            
    st.markdown("---")
    if st.button("⬅ BACK TO CONTROL ROOM"):
        navigate_func("simulator")


