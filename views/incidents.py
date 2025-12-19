import streamlit as st
import pandas as pd
import plotly.express as px
import time
from logic.scenarios.historical import SCENARIOS
from logic.engine import ReactorUnit, ReactorType
from services.reporting import ReportGenerator
from logic.visuals import VisualGenerator

def show_live_reconstruction(scenario, navigate_func):
    """Real-time synced reconstruction UI."""
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

    unit = st.session_state.replay_unit
    
    # --- CONTROLS ---
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    if c1.button("▶ PLAY" if not st.session_state.replay_running else "⏸ PAUSE"):
        st.session_state.replay_running = not st.session_state.replay_running
        
    if c2.button("🔄 RESTART"):
        unit.time_seconds = 0
        unit.event_log = []
        st.rerun()

    if c3.button("🛑 STOP"):
        st.session_state.selected_incident = None
        st.session_state.replay_unit = None
        st.rerun()

    if c4.button("⚡ TAKE CONTROL (DIVERGENT HISTORY)", type="primary"):
        # Hand over this unit to the main simulator
        unit.is_replay = False
        st.session_state.engine.units["A"] = unit
        st.session_state.active_unit_id = "A"
        navigate_func("simulator")
        st.rerun()

    # --- SIMULATION LOOP ---
    if st.session_state.replay_running:
        unit.tick(1.0)
        time.sleep(0.1) # Smoothish
        st.rerun()

    # --- DASHBOARD ---
    col_vis, col_data = st.columns([1, 1])
    
    with col_vis:
        st.markdown("### 📽️ REACTOR STATUS")
        st.write(VisualGenerator.get_reactor_svg(unit.telemetry, unit.type), unsafe_allow_html=True)
        
        # Historical Phase Indicator
        curr_phase = scenario.phases[0]
        for p in scenario.phases:
            if p['time'] <= unit.time_seconds:
                curr_phase = p
        
        st.warning(f"**HISTORICAL CONTEXT:** {curr_phase['label']} (T+{curr_phase['time']}s)")
        st.info(curr_phase['desc'])

    with col_data:
        st.markdown(f"### 📊 TELEMETRY (T+{unit.time_seconds:.1f}s)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Power", f"{unit.telemetry['power_mw']:.1f} MW")
        m2.metric("Temp", f"{unit.telemetry['temp']:.1f} °C")
        m3.metric("Health", f"{unit.telemetry['health']:.1f}%")
        
        # Events
        st.markdown("### 📜 SEQUENCE")
        for e in reversed(unit.event_log[-5:]):
            st.caption(f"[{e['time']:.1f}s] {e['event']}")

    st.markdown("---")
    # Graphs
    if unit.history:
        df = pd.DataFrame(unit.history)
        fig = px.line(df, x="time_seconds", y=["power_mw", "temp"], title="Real-time Reconstruction Data")
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)

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
        mock_unit = type('Mock', (), {
            'name': scenario.title,
            'type': type('Type', (), {'name': scenario.id.upper()}),
            'telemetry': t,
            'event_log': [{"time": p['time'], "event": f"{p['label']}: {p['desc']}"} for p in scenario.phases],
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


