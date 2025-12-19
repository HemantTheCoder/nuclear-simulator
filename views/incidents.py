import streamlit as st
import pandas as pd
import plotly.express as px
from logic.scenarios.historical import SCENARIOS
from services.reporting import ReportGenerator

def show_reconstruction(scenario, navigate_func):
    """Deep-dive UI for a specific historical incident."""
    st.markdown(f"## 🕵️ FORENSIC RECONSTRUCTION: {scenario.title}")
    
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
        # Build sequence table for graphing
        history = []
        for phase in scenario.phases:
            d = phase['telemetry'].copy()
            d['time'] = phase['time']
            d['label'] = phase['label']
            history.append(d)
        
        df = pd.DataFrame(history)
        fig = px.line(df, x="time", y=["power_mw", "temp"], title="Accident Evolution")
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### ☢️ FINAL CONSEQUENCES")
        last_phase = scenario.phases[-1]
        t = last_phase['telemetry']
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Peak Temp", f"{t.get('temp', 0)}°C")
        m2.metric("Rad Release", f"{t.get('radiation_released', 0)} Sv")
        m3.metric("Status", "MELTDOWN" if t.get('melted') else "STABLE")
        
        st.markdown("---")
        # Forensic Report Download
        # Create a dummy unit with this state for the report generator
        class MockUnit:
            def __init__(self, scenario):
                self.name = scenario.title
                self.type = type('type', (), {'name': scenario.id.upper()})
                self.telemetry = scenario.phases[-1]['telemetry']
                self.event_log = [{"time": p['time'], "event": f"{p['label']}: {p['desc']}"} for p in scenario.phases]
                self.post_mortem_report = {
                    "explanation": scenario.phases[-1]['analysis'],
                    "prevention": ["Better training", "Improved design", "Independent safety override"]
                }
                self.history = history
        
        mock_unit = MockUnit(scenario)
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
        st.rerun()

def show(navigate_func):
    """Main Incident Library View."""
    if "selected_incident" not in st.session_state:
        st.session_state.selected_incident = None
        
    if st.session_state.selected_incident:
        show_reconstruction(st.session_state.selected_incident, navigate_func)
        return

    st.markdown("## 🏛 HISTORICAL INCIDENT LIBRARY")
    st.markdown("Select a major event for a professional-grade forensic analysis.")
    
    st.info("These reconstructions use the high-fidelity simulator engine to analyze historical telemetry and failure cascades.")
    
    # 2. INCIDENT GRID
    st.markdown("---")
    
    for key, sc in SCENARIOS.items():
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                st.title("☢️" if key == "chernobyl" else "⚠️" if key=="tmi" else "🌊")
            with c2:
                st.markdown(f"### {sc.title}")
                st.write(sc.description)
                if st.button(f"OPEN FORENSIC CASE: {sc.id.upper()}", key=f"btn_{key}"):
                    st.session_state.selected_incident = sc
                    st.rerun()
            
    st.markdown("---")
    if st.button("⬅ BACK TO CONTROL ROOM"):
        navigate_func("simulator")

