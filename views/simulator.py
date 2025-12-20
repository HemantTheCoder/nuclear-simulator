import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime
from logic.engine import ReactorEngine, ReactorType
from logic.visuals import VisualGenerator
from logic.instructor import Instructor
from views.components.audio import render_audio_engine
from views.components.ui import render_annunciator_panel, render_event_log
from services.reporting import ReportGenerator

# Removed render_annunciator_panel (moved to views.components.ui)

def show(navigate_func):
    # --- 1. Init Reactor Engine (Handled globally in app.py) ---
    engine = st.session_state.get('engine')
    if not engine:
        st.session_state.engine = ReactorEngine()
        engine = st.session_state.engine
        
    if 'selected_container' not in st.session_state:
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
            
            label = f"{status_color} {data['name']}"
            if st.button(label, key=f"sel_{u_id}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_container = u_id
                st.rerun()

    if st.button("🔄 RESTORE ORIGINAL TRAINING FLEET", use_container_width=True):
        engine.reinitialize_fleet()
        st.session_state.selected_container = "A"
        st.rerun()

    st.markdown("---")
    
    # --- 3. GLOBAL CONTROLS ---
    c_mode, c_run = st.columns([2, 1])
    with c_mode:
        flight_mode = st.radio("Mode", ["Monitor", "Control Panel"], index=1, horizontal=True, label_visibility="collapsed")
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
        # Instructor
        msgs = Instructor.analyze(unit)
        if msgs:
            with st.expander("👨‍🏫 INSTRUCTOR REMARKS", expanded=True):
                for m in msgs:
                    if m["type"] == "danger": st.error(m["msg"])
                    elif m["type"] == "warning": st.warning(m["msg"])
                    else: st.info(m["msg"])

        st.markdown("### CORE STATUS")
        render_annunciator_panel(telemetry)
        
        # Audio Engine
        render_audio_engine(telemetry, sound_enabled)
        
        # Live Event Log
        render_event_log(unit.event_log)
        
        # SVG Visual
        svg_context = telemetry.copy()
        svg_context.update(controls)
        svg_context["type"] = r_type
        svg_context["melted"] = telemetry.get("melted", False)
        
        svg = VisualGenerator.get_reactor_svg(svg_context)
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{b64_svg}" style="width:100%; max-height:400px;"></div>', unsafe_allow_html=True)

        # Telemetry Ribbon
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Pwr", f"{telemetry['power_mw']:.0f} MW")
        m2.metric("Temp", f"{telemetry['temp']:.0f} °C")
        m3.metric("Press", f"{telemetry.get('pressure',0):.1f} Bar")
        m4.metric("Lvl", f"{telemetry.get('water_level',5):.1f} m")
        m5.metric("Load", f"{controls.get('turbine_load_mw', 1000.0):.0f} MW")
        
        # Radiation Monitor
        rads = telemetry.get('radiation_released', 0)
        if rads > 0:
            st.metric("☢️ RAD RELEASE", f"{rads:.2f} Sv", delta_color="inverse")

        with st.expander("🛠️ TECHNICAL ANALYSIS (NEUTRONICS)", expanded=False):
            rc = telemetry.get("reactivity_components", {})
            c_rho1, c_rho2, c_rho3, c_rho4 = st.columns(4)
            c_rho1.metric("Net Rho", f"{telemetry['reactivity']*10000:.0f} pcm")
            c_rho2.metric("Rod Worth", f"{rc.get('rods',0)*10000:.0f} pcm")
            c_rho3.metric("Void Coeff", f"{rc.get('void',0)*10000:.0f} pcm")
            c_rho4.metric("Doppler", f"{rc.get('doppler',0)*10000:.0f} pcm")
            
            c_rho5, c_rho6, c_rho7 = st.columns(3)
            c_rho5.metric("Xenon Poison", f"{rc.get('xenon',0)*10000:.0f} pcm")
            c_rho6.metric("Boron Poison", f"{rc.get('boron',0)*10000:.0f} pcm")
            c_rho7.metric("Period", f"{telemetry.get('period', 999):.1f} s")
            
            st.divider()
            st.caption("🌊 THERMAL HYDRAULICS & SAFETY MARGINS")
            c_th1, c_th2, c_th3, c_th4 = st.columns(4)
            c_th1.metric("Mass Flow", f"{telemetry.get('mass_flow', 0)/1000.0:.1f} t/s")
            c_th2.metric("T-Inlet", f"{telemetry.get('t_inlet', 0):.1f} °C")
            c_th3.metric("T-Outlet", f"{telemetry.get('t_outlet', 0):.1f} °C")
            
            dnbr = telemetry.get('dnbr', 99.9)
            dnbr_delta = "CRITICAL" if dnbr < 1.3 else "SAFE"
            c_th4.metric("DNBR", f"{dnbr:.2f}", delta=dnbr_delta, delta_color="normal" if dnbr > 1.3 else "inverse")


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
                if report.get("prevention"):
                    st.success(f"**PREVENTION:** {report['prevention']}")
            
            with c2:
                st.markdown("### ⏱️ EVENTS")
                for e in report["timeline"]:
                    st.markdown(f"`T+{e['time']:.1f}s` : {e['event']}")
        
        if st.button(f"RESET {unit.name} (NOMINAL)"):
             unit.reset()
             st.rerun()
             
        # New: Forensic Download
        # New: Forensic Download
        if st.checkbox("📄 GENERATE FORENSIC REPORT"):
            with st.spinner("Compiling Forensic Data..."):
                pdf_data = ReportGenerator.generate_pdf(unit, unit.history)
                
            st.download_button(
                label="📥 DOWNLOAD PDF",
                data=pdf_data,
                file_name=f"ACCIDENT_REPORT_{unit.name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
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
            col_r1, col_r2 = st.columns([2, 1])
            rod_label = "Control Rods Insertion"
            new_controls["rods_pos"] = col_r1.slider(rod_label, 0.0, 100.0, controls["rods_pos"], key="rod_slider")
            
            new_controls["auto_rod_control"] = col_r2.toggle("AUTO PILOT", value=controls.get("auto_rod_control", False))
            if new_controls["auto_rod_control"]:
                 st.caption("🤖 Maintaining Load")
            
            # 2. Flow/Cooling
            st.markdown("**COOLANT SYSTEM**")
            new_controls["pump_speed"] = st.slider("Main Pump Speed (%)", 0.0, 100.0, controls["pump_speed"], key="pump_slider")

            # 2.5 Turbine Logic
            st.markdown("**TURBINE & STEAM**")
            new_controls["turbine_load_mw"] = st.slider("Turbine Load Demand (MW)", 0.0, 3500.0, controls.get("turbine_load_mw", 1000.0))
            new_controls["msiv_open"] = st.toggle("MSIV (Main Steam Isolation Valves)", value=controls.get("msiv_open", True))
            
            if not new_controls["msiv_open"]:
                st.error("⚠️ STEAM ISOLATED - PRESSURE SPIKE IMMINENT")
            
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
            if st.button("🔄 RESET UNIT TO NOMINAL"):
                unit.reset()
                st.rerun()
            
            # New: Session Report
            # New: Session Report
            st.markdown("---")
            if st.checkbox("📥 PREPARE SESSION REPORT"):
                 with st.spinner("Compiling Report..."):
                    pdf_data = ReportGenerator.generate_pdf(unit, unit.history)
                 
                 st.download_button(
                    label="📄 DOWNLOAD PDF",
                    data=pdf_data,
                    file_name=f"SESSION_{unit.name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            if new_controls != controls:
                # Log the User Action
                for key, val in new_controls.items():
                    if controls.get(key) != val:
                        # Format value for readability
                        val_str = f"{val:.1f}" if isinstance(val, float) else str(val)
                        unit.log_event(f"USER: Set {key} to {val_str}")
                        
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
        st.line_chart(df, x="time_seconds", y=["power_mw", "temp"])
    
    # Auto Run Tick
    if auto_run:
        time.sleep(0.1)
        engine.tick(0.1)
        st.rerun()
