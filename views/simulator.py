import streamlit as st
import pandas as pd
import base64
import time
from logic.engine import ReactorEngine, ReactorType
from logic.visuals import VisualGenerator
from views import god_mode
from views.components.audio import render_audio_engine

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
            engine.tick(1.0)
            st.rerun()

    # --- AUDIO & SETTINGS ---
    with st.sidebar:
        st.markdown("### ⚙️ SETTINGS")
        sound_enabled = st.checkbox("🔊 Enable Sound Effects", value=True)
        
        st.markdown("---")
        with st.expander("📖 OPERATOR MANUAL"):
            st.markdown("""
            **SYSTEM REFERENCE**
            
            **REACTOR TYPES**
            - **PWR**: Stable. Monitor **Pressurizer**. Use **Heaters** to raise pressure, **Sprays** to lower it. Use **Boron** for long-term power changes.
            - **BWR**: Boiling is normal. Control **Feedwater** to keep level stable. Open **Turbine Bypass** if pressure spikes.
            - **RBMK**: Unstable at low power ("Positive Void Coefficient"). Keep **Drum Level** high. **Avoid sudden control rod insertion** (Tip Effect).
            
            **SAFETY**
            - **SCRAM**: Emergency Shutdown.
            - **ECCS**: Emergency Cooling. Saves fuel, shocks vessel.
            - **VENT**: Releases pressure & radiation.
            """)

    if flight_mode == "God Mode 👁️":
        god_mode.show()
        return

    # --- 4. MAIN DASHBOARD ---
    selected_id = st.session_state.selected_container
    unit = engine.units[selected_id] # Access actual object for advanced props
    data = states[selected_id]
    telemetry = data['telemetry']
    controls = data['controls']
    r_type = data.get("type", "PWR")
    
    # Layout: Annunciator | Visuals | Controls
    col_vis, col_ctrl = st.columns([1.5, 1.2])
    
    with col_vis:
        st.markdown("### CORE STATUS")
        render_annunciator_panel(telemetry)
        
        # Audio Engine
        render_audio_engine(telemetry, sound_enabled)
        
        # Live Event Log
        with st.container(border=True):
            st.markdown("**📜 LIVE EVENT LOG**")
            events = unit.event_log[-5:] # Show last 5
            for e in reversed(events):
                st.markdown(f"`T+{e['time']:.0f}s`: {e['event']}")
            if not events:
                st.caption("No recent events.")
        
        # SVG Visual
        svg = VisualGenerator.get_reactor_svg({
            "type": r_type,
            "temp": telemetry["temp"],
            "flux": telemetry["flux"],
            "rods_pos": controls["rods_pos"],
            "void_fraction": telemetry.get("void_fraction", 0.0),
            "scram": telemetry.get("scram", False),
            "melted": telemetry.get("melted", False)
        })
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{b64_svg}" style="width:100%; max-height:400px;"></div>', unsafe_allow_html=True)

        # Telemetry Ribbon
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Pwr", f"{telemetry['power_mw']:.0f} MW")
        m2.metric("Temp", f"{telemetry['temp']:.0f} °C")
        m3.metric("Press", f"{telemetry.get('pressure',0):.1f} Bar")
        m4.metric("Lvl", f"{telemetry.get('water_level',5):.1f} m")
        
        # Radiation Monitor
        rads = telemetry.get('radiation_released', 0)
        if rads > 0:
            st.metric("☢️ RAD RELEASE", f"{rads:.2f} Sv", delta_color="inverse")


    # CHECK FOR DEATH
    if telemetry.get("health", 100) <= 0:
        st.markdown("---")
        st.error(f"# ☠️ MISSION FAILED: {unit.failure_cause}")
        
        report = getattr(unit, "post_mortem_report", None)
        if report:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("### 🔬 ACCIDENT ANALYSIS")
                st.info(report["explanation"])
                if report["prevention"]:
                    st.success(f"**PREVENTION:** {report['prevention']}")
            
            with c2:
                st.markdown("### ⏱️ EVENTS")
                for e in report["timeline"]:
                    st.markdown(f"`T+{e['time']:.1f}s` : {e['event']}")
        
        if st.button(f"RESET {unit.name} (COLD SHUTDOWN)"):
             unit.reset()
             st.rerun()
        
        return # STOP RENDERING CONTROLS

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
            st.markdown("**SYSTEM CONFIG**")
            
            if r_type == "PWR":
                st.info("ℹ️ CHEMICAL SHIM & PRESSURE")
                # Boron
                new_controls["boron_concentration"] = st.slider("Boron (ppm)", 0.0, 2000.0, controls.get("boron_concentration", 1000.0), 10.0)
                
                # Pressurizer
                c_p1, c_p2 = st.columns(2)
                new_controls["pressurizer_heaters"] = c_p1.toggle("Heaters", controls.get("pressurizer_heaters", False))
                new_controls["pressurizer_sprays"] = c_p2.toggle("Sprays", controls.get("pressurizer_sprays", False))
                
            elif r_type == "BWR":
                st.info("ℹ️ WATER LEVEL & BYPASS")
                st.metric("Steam Voids", f"{telemetry.get('void_fraction',0)*100:.1f}%")
                
                # Feedwater
                new_controls["feedwater_flow"] = st.slider("Feedwater Flow (%)", 0.0, 150.0, controls.get("feedwater_flow", 100.0))
                
                # Bypass
                new_controls["turbine_bypass"] = st.slider("Turbine Bypass (%)", 0.0, 100.0, controls.get("turbine_bypass", 0.0))
                
            elif r_type == "RBMK":
                st.warning("⚠️ DRUM SEPARATORS")
                col_d1, col_d2 = st.columns(2)
                col_d1.metric("Drum Level", f"{telemetry.get('water_level',5):.2f}m")
                col_d2.metric("Xenon", f"{telemetry.get('xenon',1.0):.2f}")
                
                 # Feedwater
                new_controls["feedwater_flow"] = st.slider("Feedwater (Drum Fill)", 0.0, 150.0, controls.get("feedwater_flow", 100.0))

            # Interlocks
            new_controls["safety_enabled"] = st.checkbox("Safety Interlocks Enabled", value=controls["safety_enabled"])

            st.markdown("---")
            st.markdown("### 🚨 EMERGENCY OVERRIDES")
            c_e1, c_e2 = st.columns(2)
            
            # ECCS
            eccs_active = controls.get("eccs_active", False)
            if c_e1.button("ACTUATE ECCS", type="primary" if not eccs_active else "secondary"):
                new_controls["eccs_active"] = not eccs_active
                st.toast("ECCS INJECTION TOGGLED" if not eccs_active else "ECCS SECURED")
            
            if eccs_active: st.warning("ECCS INJECTING - THERMAL SHOCK RISK")

            # Vent
            if c_e2.button("MANUAL VENT"):
                new_controls["manual_vent"] = True
                new_controls["eccs_active"] = controls.get("eccs_active", False) # Preserve state
                
            # One-shot vent reset handled by logic layer usually, but here we just need to set it to True for a tick?
            # Ideally simulator is loop based.
            # State based toggle is better for streamlit.
            new_controls["manual_vent"] = st.toggle("OPEN VENT VALVES (RELEASE RADS)", value=controls.get("manual_vent", False))
            
            if new_controls["manual_vent"]:
                 st.error("⚠️ VENTING TO ATMOSPHERE")
            
            st.markdown("---")
            if st.button("🔄 RESET UNIT TO INITIAL STATE"):
                unit.reset()
                st.rerun()

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
