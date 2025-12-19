import streamlit as st
import pandas as pd
import base64
from logic.engine import ReactorEngine
from logic.visuals import VisualGenerator
import time
from views import god_mode

def show(navigate_func):
    # --- 1. Init Reactor Engine ---
    if 'engine' not in st.session_state or not isinstance(st.session_state.engine, ReactorEngine):
        st.session_state.engine = ReactorEngine()
        st.session_state.selected_container = "A"
        st.session_state.active_control_tab = "Physics"
    
    engine = st.session_state.engine
    states = engine.get_all_states()
    
    # --- 2. REACTOR STATUS HEADER ---
    st.markdown("## ☢️ NUCLEAR CONTROL ROOM")
    
    # Unit Selector
    cols = st.columns(3)
    unit_ids = ["A", "B"]
    
    for i, u_id in enumerate(unit_ids):
        data = states[u_id]
        telemetry = data['telemetry']
        is_selected = (st.session_state.selected_container == u_id)
        
        with cols[i]:
            status_icon = "🟢" if telemetry['temp'] < 400 else ("🔴" if telemetry['temp'] > 600 else "🟠")
            
            # Mini Visual
            svg = VisualGenerator.get_reactor_svg({
                "temp": telemetry["temp"],
                "flux": telemetry["flux"],
                "rods": data['controls']["rods_pos"]
            })
            b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
            st.markdown(f'<div style="text-align:center; margin-bottom:5px;"><img src="data:image/svg+xml;base64,{b64_svg}" style="width:50px; height:60px;"></div>', unsafe_allow_html=True)
            
            label = f"{status_icon} {data['name']} {telemetry['power_mw']:.0f}MW"
            if st.button(label, key=f"sel_{u_id}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_container = u_id
                st.rerun()
                
    st.markdown("---")

    # --- 3. VIEW MODE & GLOBAL ACTION ---
    c_preset, c_mode, c_adv = st.columns([1.5, 1.5, 1])
    
    with c_preset:
         st.markdown("##### 🏁 SCENARIO PRESET")
         preset = st.selectbox("Select Context", ["STABLE", "VOLATILE", "DEGRADED"], label_visibility="collapsed")
         if st.button("APPLY PRESET", use_container_width=True):
             engine.units["A"].apply_preset(preset)
             st.rerun()

    with c_mode:
         # GLOBAL MODE TOGGLE
         st.markdown("##### 🎮 OPERATOR MODE")
         flight_mode = st.radio("Operator Mode", ["Monitor", "Control Panel", "God Mode 👁️"], index=1, horizontal=True, label_visibility="collapsed")
         
         
    # Check flight mode outside of column context to allow full-width rendering
    # We need to capture the value from the loop or the widget
    # The widget variable `flight_mode` is available in the local scope
    
    if flight_mode == "God Mode 👁️":
        god_mode.show()
        return # Halt execution of standard panel

    is_control = (flight_mode == "Control Panel")
         
    with c_adv:
        # Time Control (Auto-Run)
        st.markdown("##### ⏱ CLOCK")
        auto_run = st.toggle("AUTO RUN", value=st.session_state.get("auto_run", False), key="auto_run_toggle")
        
        if st.button("STEP (+1s)", use_container_width=True):
             engine.tick(dt=1.0)
             st.rerun()

    # --- 4. FOCUS VIEW (CONTROL ROOM) ---
    selected_id = st.session_state.selected_container
    data = states[selected_id]
    telemetry = data['telemetry']
    controls = data['controls']
    
    # 4a. CAUSE -> EFFECT RIBBON (Visual Physics Engine)
    # Determine active step based on state
    step = 1 # Nominal
    if telemetry['reactivity'] > 0.0005: step = 2 # Reactivity Spike
    if telemetry['flux'] > 1.2: step = 3 # Power Excursion
    if telemetry['temp'] > 400: step = 4 # Heat Buildup
    if telemetry['reactivity'] < 0: step = 5 # Feedback/Scram
    
    st.markdown(f"""
    <div class="cause-ribbon-container">
        <div class="cause-step {'active' if step==1 else ''}">CORE STABLE</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if step==2 else ''}">REACTIVITY ↑</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if step==3 else ''}">POWER ↑</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if step==4 else ''}">HEAT ↑</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if step==5 else ''}">FEEDBACK (VOID/DOPPLER)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # TOP BAR
    c1, c2, c3 = st.columns([1, 1, 2])
    # Safe Time Access
    hist = data.get('history', [])
    last_time = hist[-1].get('time', 0) if hist else 0
    c1.metric("Sim Time", f"{last_time} s")
    c2.metric("Core State", "CRITICAL" if telemetry['flux'] > 0 else "SHUTDOWN")
    
    with c3:
        if telemetry['alerts']:
            st.error(" | ".join(telemetry['alerts']))
        else:
            # Health Bar
            health = telemetry.get('health', 100.0)
            color = "green" if health > 80 else ("orange" if health > 50 else "red")
            st.markdown(f"**STRUCTURAL INTEGRITY:** <span style='color:{color}'>{health:.1f}%</span>", unsafe_allow_html=True)
            st.progress(health / 100.0)
    
    st.markdown("---")
    
    # LAYOUT: LEFT (Controls), CENTER (Core), RIGHT (Meters)
    col_ctrl, col_core, col_met = st.columns([1.2, 1.5, 1.3])
    
    # --- LEFT: CONTROLS ---
    with col_ctrl:
        st.markdown("### 🎛 CONTROLS")
    
        if not is_control:
             st.info("System in Monitor Mode.")
             st.markdown("<div style='opacity:0.6; pointer-events:none;'>", unsafe_allow_html=True)

        new_controls = controls.copy()
        
        # Scram Button (Always Valid)
        if st.button("🛑 SCRAM SWITCH", type="primary", use_container_width=True):
             new_controls["manual_scram"] = True
             engine.update_controls(selected_id, new_controls)
             new_controls["manual_scram"] = True
             engine.update_controls(selected_id, new_controls)
             st.rerun()
             
        st.markdown("---")
        
        # Physics Control
        st.markdown("**REACTIVITY** <span class='delay-badge'>~0.5s Lag</span>", unsafe_allow_html=True)
        new_controls["rods_pos"] = st.slider("Control Rods Insertion (%)", 0.0, 100.0, controls["rods_pos"], key="rod_sl")
        st.caption("0% = Max Power | 100% = Shutdown")
        
        st.markdown("**COOLING** <span class='delay-badge'>~3.0s Lag</span>", unsafe_allow_html=True)
        new_controls["pump_speed"] = st.slider("Primary Pump Speed (%)", 0.0, 100.0, controls["pump_speed"])
        new_controls["cooling_eff"] = st.slider("Heat Exchanger Eff (%)", 0.0, 100.0, controls["cooling_eff"])
        
        # Safety Override
        new_controls["safety_enabled"] = st.toggle("Safety Interlocks", value=controls["safety_enabled"])
        if not new_controls["safety_enabled"]:
            st.warning("⚠️ INTERLOCKS DISABLED")

        if not is_control:
             st.markdown("</div>", unsafe_allow_html=True)
             
        if new_controls != controls:
             engine.update_controls(selected_id, new_controls)
             st.rerun()

        # ENGINEERING TAB (Advanced Physics)
        st.markdown("---")
        with st.expander("🛠 ENGINEERING CONFIG", expanded=False):
            # 1. Physics Tuning
            st.markdown("##### PHYSICS TUNING")
            conf = data['config'] if 'config' in data else engine.units[selected_id].config # Fallback
            
            new_conf = {}
            new_conf['responsiveness'] = st.slider("Responsiveness (Damping)", 0.5, 2.0, conf.responsiveness, 0.1, help="Higher = Twitchy, Lower = Sluggish")
            new_conf['thermal_inertia'] = st.slider("Thermal Inertia", 0.5, 5.0, conf.thermal_inertia, 0.1, help="Higher = Slower Temp Change")
            new_conf['feedback_strength'] = st.slider("Feedback Strength", 0.0, 2.0, conf.feedback_strength, 0.1, help="Higher = Stronger Self-Stabilization")
            
            if new_conf['responsiveness'] != conf.responsiveness or new_conf['thermal_inertia'] != conf.thermal_inertia or new_conf['feedback_strength'] != conf.feedback_strength:
                engine.update_config(selected_id, new_conf)
                st.rerun()

            st.markdown("---")
            # 2. Disturbances
            st.markdown("##### STRESS TESTS")
            c_d1, c_d2, c_d3 = st.columns(3)
            if c_d1.button("⚡ FLUX SPIKE"):
                engine.inject_disturbance(selected_id, "SPIKE")
                st.toast("Injecting Reactivity Spike...", icon="⚡")
            if c_d2.button("❄️ PUMP FAIL"):
                engine.inject_disturbance(selected_id, "COOLING_FAIL")
                st.toast("Primary Pump Efficiency Reduced!", icon="⚠️")
            if c_d3.button("🔄 RESET ALL"):
                engine.inject_disturbance(selected_id, "RESET")
                st.toast("System Nominal. Disturbances cleared.", icon="✅")

    # --- CENTER: REACTOR CORE VISUAL ---
    with col_core:
        st.markdown(f"<div style='text-align:center'><b>{data['name']} REACTOR VESSEL</b></div>", unsafe_allow_html=True)
        # Pass telemetry directly to visual generator
        svg = VisualGenerator.get_reactor_svg({
            "temp": telemetry["temp"],
            "flux": telemetry["flux"],
            "rods": controls["rods_pos"]
        })
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        # Tension Pulse Class Logic
        tension_class = "tension-active" if telemetry.get('stability_margin', 100) < 40 else ""
        
        st.markdown(f"""
        <div class="reactor-container {tension_class}">
            <div style="font-weight:bold; margin-bottom:10px; color:#aaa; letter-spacing:2px;">{data['name']} VESSEL</div>
            <img src="data:image/svg+xml;base64,{b64_svg}" style="width: 100%; height: 400px; filter: drop-shadow(0 0 10px rgba(52, 152, 219, 0.3));">
        </div>
        """, unsafe_allow_html=True)

    # --- RIGHT: TELEMETRY ---
    with col_met:
        st.markdown("### 📊 SENSORS")
        
        st.metric("Thermal Power", f"{telemetry['power_mw']:.1f} MW", delta=f"{telemetry['flux']*100:.1f}% Flux")
        st.metric("Core Temperature", f"{telemetry['temp']:.1f} °C", delta=f"{(telemetry['temp']-300):.1f} Delta")
        
        reactivity_pcm = telemetry['reactivity'] * 100000 
        st.metric("Reactivity", f"{reactivity_pcm:.1f} pcm")
        
        period = telemetry['period']
        p_str = f"{period:.1f} s" if period < 999 else "INF"
        st.metric("Reactor Period", p_str)
        
        # Custom Telemetry HTML for Trends (Replaces standard metric for deeper immersion)
        def trend_html(label, val, unit, trend_class):
            return f"""
            <div style="background:#222; border:1px solid #333; padding:10px; margin-bottom:5px; border-radius:5px;">
                <div style="font-size:0.8em; color:#888;">{label}</div>
                <div class="telemetry-val {trend_class}">
                    {val} <span style="font-size:0.6em; color:#aaa; margin-left:5px;">{unit}</span>
                </div>
            </div>
            """
        
        # Determine trends
        p_trend = "trend-up" if telemetry['power_mw'] > 1000 else ("trend-flat" if telemetry['power_mw'] > 0 else "trend-down")
        if telemetry['scram']: p_trend = "trend-down"
        
        st.markdown(trend_html("THERMAL POWER", f"{telemetry['power_mw']:.1f}", "MW", p_trend), unsafe_allow_html=True)
        st.markdown(trend_html("CORE TEMP", f"{telemetry['temp']:.1f}", "°C", "trend-up" if telemetry['temp'] > 600 else "trend-flat"), unsafe_allow_html=True)
        
        st.markdown("---")
        if telemetry['scram']:
            st.error("REACTOR TRIPPED (SCRAM)")
        elif telemetry['temp'] > 400:
            st.warning("TEMP WARNING")
        else:
            st.success("OPERATING NORMALLY")

    # --- BOTTOM: GRAPHS ---
    st.markdown("### 📈 RECORDER TRACE")
    if len(data['history']) > 2:
        df = pd.DataFrame(data['history'])
        c1, c2 = st.columns(2)
        with c1:
            st.line_chart(df, x="time", y="power", height=200)
        with c2:
            st.line_chart(df, x="time", y="temp", height=200)
    else:
        st.info("Insufficient data. Start simulation clock.")

    # --- AUTO RUN LOGIC (Must be last to ensure UI renders first) ---
    if auto_run:
        time.sleep(0.5) # Reduced for smoother feel
        engine.tick(dt=1.0) # Sim moves 1s per 0.5s real time
        st.rerun()
