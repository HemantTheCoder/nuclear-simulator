import streamlit as st
import pandas as pd

def show(navigate_func):
    st.markdown("## 📈 SYSTEM ANALYTICS & LOGS")
    
    st.info("Performance analysis across historical incidents and user simulation runs.")
    
    engine = st.session_state.engine
    states = engine.get_all_states()
    
    # 1. CURRENT RUN STATISTICS
    st.markdown("### 🟢 ACTIVE SESSION DATA")
    u_id = st.session_state.selected_container
    data = states[u_id]
    
    if len(data['history']) > 0:
        df = pd.DataFrame(data['history'])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peak Power", f"{df['power'].max():.1f} MW")
        c2.metric("Max Temp", f"{df['temp'].max():.1f} °C")
        c3.metric("Duration", f"{df['time'].iloc[-1]:.0f} s")
        
        st.markdown("#### Power Dynamics")
        st.line_chart(df, x="time", y="power")
        
        st.markdown("#### Thermal Stability")
        st.line_chart(df, x="time", y="temp")
        
        st.markdown("#### Reactivity Excursions (pcm)")
        st.line_chart(df, x="time", y="reactivity")
    else:
        st.warning("No data recorded in current session.")
        
    st.markdown("---")
    
    # 2. INCIDENT COMPARISON
    st.markdown("### ⚔️ HISTORICAL COMPARISON")
    
    # Simple static comparison data for demo
    comp_data = pd.DataFrame({
        "Metric": ["Peak Power", "Time to Failure", "Max Reactivity"],
        "Chernobyl (1986)": ["30,000 MW", "60s", "+400 pcm"],
        "Current Run": [
            f"{df['power'].max():.1f} MW" if len(data['history'])>0 else "-",
            f"{df['time'].iloc[-1]:.0f} s" if len(data['history'])>0 else "-",
            f"{df['reactivity'].max():.0f} pcm" if len(data['history'])>0 else "-"
        ]
    })
    st.table(comp_data)
    
    st.markdown("---")
    
    # 3. REPORT GENERATION
    st.markdown("### 📄 GENERATE REPORT")
    
    from services.reporting import ReportGenerator
    
    html_report = ReportGenerator.generate_html_report(data, session_name=f"RUN-{u_id}-LOG")
    st.download_button(
        label="DOWNLOAD FULL ANALYSIS (HTML)",
        data=html_report,
        file_name="Simulation_Log.html",
        mime="text/html",
        type="primary"
    )
