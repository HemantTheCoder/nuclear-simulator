import streamlit as st
import pandas as pd
import base64
import time
from logic.engine import ReactorEngine, ReactorType
from logic.visuals import VisualGenerator
from views import god_mode

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
        "VOID ALRM": telemetry.get("void_fraction", 0) > 0.4
    }
    
    st.markdown("""
    <style>
    .annunciator-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
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
    <div class="annunciator-grid">
    """, unsafe_allow_html=True)
    
    html = '<div class="annunciator-grid">'
    for label, active in alerts.items():
        cls = "alarm-active" if active else ""
        html += f'<div class="alarm-box {cls}">{label}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def show(navigate_func):
    # --- 1. Init Reactor Engine ---
    if 'engine' not in st.session_state or not isinstance(st.session_state.engine, ReactorEngine):
        st.session_state.engine = ReactorEngine()
        st.session_state.selected_container = "A"
    
    engine = st.session_state.engine
    states = engine.get_all_states()
    
    # --- 2. HEADER & SELECTION ---
    st.markdown("## ☢️ NUCLEAR CONTROL ROOM")
    
    # Unit Selector Logic
    cols = st.columns(3)
    unit_ids = ["A", "B", "C"]
    
    for i, u_id in enumerate(unit_ids):
        if u_id not in states: continue
        data = states[u_id]
        telemetry = data['telemetry']
        r_type = data.get("type", "PWR")
        is_selected = (st.session_state.selected_container == u_id)
        
        with cols[i]:
            status_color = "🟢" if telemetry['temp'] < 600 else "🔴"
            if telemetry['scram']: status_color = "⚫"
            
            label = f"{status_color} {data['name']} [{r_type}]"
            if st.button(label, key=f"sel_{u_id}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_container = u_id
                st.rerun()

    st.markdown("---")
    
    # --- 3. GLOBAL CONTROLS ---
    c_mode, c_run = st.columns([2, 1])
    with c_mode:
        flight_mode = st.radio("Mode", ["Monitor", "Control Panel", "God Mode 👁️"], index=1, horizontal=True, label_visibility="collapsed")
    with c_run:
        auto_run = st.toggle("AUTO RUN (1x)", value=st.session_state.get("auto_run", False), key="auto_run_toggle")
        if st.button("STEP (+1s)"):
            engine.tick(1.0)
            st.rerun()

    if flight_mode == "God Mode 👁️":
        god_mode.show()
        return

    # --- 4. MAIN DASHBOARD ---
    selected_id = st.session_state.selected_container
    data = states[selected_id]
    telemetry = data['telemetry']
    controls = data['controls']
    r_type = data.get("type", "PWR")
    
    # Layout: Annunciator | Visuals | Controls
    col_vis, col_ctrl = st.columns([1.5, 1.2])
    
    with col_vis:
        st.markdown("### CORE STATUS")
        render_annunciator_panel(telemetry)
        
        # SVG Visual
        svg = VisualGenerator.get_reactor_svg({
            "type": r_type,
            "temp": telemetry["temp"],
            "flux": telemetry["flux"],
            "rods_pos": controls["rods_pos"],
            "void_fraction": telemetry.get("void_fraction", 0.0),
            "scram": telemetry.get("scram", False)
        })
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{b64_svg}" style="width:100%; max-height:400px;"></div>', unsafe_allow_html=True)

        # Telemetry Ribbon
        m1, m2, m3 = st.columns(3)
        m1.metric("Thermal Power", f"{telemetry['power_mw']:.0f} MW", f"{telemetry['flux']*100:.1f}%")
        m2.metric("Core Temp", f"{telemetry['temp']:.0f} °C", f"{(telemetry['temp']-300):.0f}")
        m3.metric("Structure", f"{telemetry['health']:.1f}%", delta_color="off")

    with col_ctrl:
        st.markdown(f"### 🎛 {r_type} CONTROL DESK")
        
        if flight_mode == "Monitor":
            st.info("Controls Locked (Monitor Mode)")
        else:
            new_controls = controls.copy()
            
            # SCRAM BUTTON
            btn_label = "AZ-5 (SCRAM)" if r_type == "RBMK" else "MANUAL SCRAM"
            if st.button(btn_label, type="primary", use_container_width=True):
                new_controls["manual_scram"] = True
                engine.update_controls(selected_id, new_controls)
                st.rerun()
            
            st.markdown("---")
            
            # CORE CONTROLS
            # 1. Rods
            st.markdown("**REACTIVITY CONTROL**")
            rod_label = "Control Rods Insertion"
            new_controls["rods_pos"] = st.slider(rod_label, 0.0, 100.0, controls["rods_pos"], key="rod_slider")
            
            # 2. Flow/Cooling
            st.markdown("**COOLANT SYSTEM**")
            new_controls["pump_speed"] = st.slider("Main Pump Speed (%)", 0.0, 100.0, controls["pump_speed"], key="pump_slider")
            
            # 3. Type Specific
            if r_type == "PWR":
                st.info("ℹ️ Maintain pressure to prevent boiling.")
            elif r_type == "BWR":
                st.info("ℹ️ Boiling is nominal. Monitor void fraction.")
                st.metric("Steam Voids", f"{telemetry.get('void_fraction',0)*100:.1f}%")
            elif r_type == "RBMK":
                st.warning("⚠️ POSITIVE VOID COEFFICIENT. Avoid low power operation.")
                st.metric("Xenon Poison", f"{telemetry.get('xenon',1.0):.2f}")

            # Interlocks
            new_controls["safety_enabled"] = st.checkbox("Safety Interlocks Enabled", value=controls["safety_enabled"])

            if new_controls != controls:
                engine.update_controls(selected_id, new_controls)
                st.rerun()

    # --- 6. PROCEDURES MANUAL ---
    with st.expander("📚 REACTOR OPERATING PROCEDURES", expanded=False):
        if r_type == "RBMK":
            st.markdown("""
            **RBMK-1000 STANDARD OPERATING PROCEDURE**
            
            **1. STARTUP**
            - Ensure Flow > 80%
            - Withdraw rods to 30%
            - **WARNING:** Avoid prolonged operation < 700 MW (Xenon Instability)
            
            **2. EMERGENCY (AZ-5)**
            - In case of runaway power or loss of coolant:
            - Press **AZ-5** immediately.
            - **CAUTION:** Early shutdown phase may induce temporary positive reactivity (Tip Effect). 
            """)
        elif r_type == "PWR":
            st.markdown("""
            **PWR STANDARD OPERATING PROCEDURE**
            
            **1. CRITICALITY**
            - Withdraw rods slowly.
            - Monitor Period (> 10s).
            - Maintain Pressure (Pressurizer Heaters ON).
            
            **2. SHUTDOWN**
            - Insert rods fully.
            - Engage Boron Injection if rods fail.
            """)
        elif r_type == "BWR":
            st.markdown("""
            **BWR STANDARD OPERATING PROCEDURE**
            
            **1. POWER ASCENSION**
            - Increase Recirculation Flow to increase Power (Void sweeping).
            - Withdraw Control Rods for shaping.
            - Monitor Steam Line Radiation.
            """)

    # --- 5. GRAPHS ---
    if len(data['history']) > 2:
        st.markdown("### 📈 FLIGHT RECORDER")
        df = pd.DataFrame(data['history'])
        st.line_chart(df, x="time", y=["power", "temp"])
    
    # Auto Run Tick
    if auto_run:
        time.sleep(0.5)
        engine.tick(1.0)
        st.rerun()
