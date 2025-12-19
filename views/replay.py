import streamlit as st
import base64
import pandas as pd
from logic.visuals import VisualGenerator
import time

def show(navigate_func):
    engine = st.session_state.engine
    states = engine.get_all_states()
    meta = states.get("scenario_meta", {})
    
    # Redirect if no scenario active
    if not meta.get("active"):
        st.warning("No incident loaded.")
        if st.button("Return to Library"): navigate_func("incidents")
        return

    # --- HEADER ---
    st.markdown(f"## 🎞 REPLAY: {meta['title']}")
    
    # --- DASHBOARD LAYOUT ---
    # CAUSE -> EFFECT RIBBON (Scenario Mode)
    st.markdown(f"""
    <div class="cause-ribbon-container">
        <div class="cause-step {'active' if meta['phase']=='Preparation' else ''}">PREPARE</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if meta['phase']=='Instability' or 'Trip' in meta['phase'] else ''}">INITIATING EVENT</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if meta['phase']=='The Surge' or 'Boil Off' in meta['phase'] or 'Loss' in meta['phase'] else ''}">CASCADE</div>
        <div class="cause-arrow">➜</div>
        <div class="cause-step {'active' if meta['phase']=='Explosion' or 'Meltdown' in meta['phase'] else ''}">CRITICAL FAILURE</div>
    </div>
    """, unsafe_allow_html=True)

    col_vis, col_info = st.columns([1.5, 2])
    
    with col_vis:
        # VISUALIZER (Using Unit A which is the actor)
        data = states["A"]
        telemetry = data["telemetry"]
        
        st.markdown(f"<div style='text-align:center; font-weight:bold;'>PHASE: {meta['phase']}</div>", unsafe_allow_html=True)
        
        svg = VisualGenerator.get_reactor_svg({
            "temp": telemetry["temp"],
            "flux": telemetry["flux"],
            "rods": data["controls"]["rods_pos"]
        })
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        st.markdown(f"""
        <div class="reactor-container">
            <div style="font-weight:bold; margin-bottom:10px; color:#aaa; letter-spacing:2px;">SCENARIO RECONSTRUCTION</div>
            <img src="data:image/svg+xml;base64,{b64_svg}" style="width: 100%; height: 350px; filter: drop-shadow(0 0 10px rgba(231, 76, 60, 0.4));">
        </div>
        """, unsafe_allow_html=True)
        
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
        
        # Determine trends (Simple logic for replay)
        p_trend = "trend-up" if telemetry['reactivity'] > 0 else "trend-flat"
        if telemetry['scram']: p_trend = "trend-down"
        
        st.markdown(trend_html("THERMAL POWER", f"{telemetry['power_mw']:.0f}", "MW", p_trend), unsafe_allow_html=True)
        st.markdown(trend_html("CORE TEMP", f"{telemetry['temp']:.0f}", "°C", "trend-up" if telemetry['temp'] > 600 else "trend-flat"), unsafe_allow_html=True)
        st.markdown(trend_html("REACTIVITY", f"{(telemetry['reactivity']*100000):.0f}", "pcm", "trend-flat"), unsafe_allow_html=True)

    with col_info:
        # TIMELINE SCRUBBER
        st.markdown("### ⏱ TIMELINE CONTROL")
        
        # Current time display
        t = meta['time']
        st.progress(min(1.0, t / 200.0)) # Assuming 200s max for now for UI scale
        
        c_ctrl1, c_ctrl2 = st.columns(2)
        with c_ctrl1:
             if st.button("⏯ PLAY / PAUSE", type="primary", use_container_width=True):
                 # Simple toggle logic for auto-run could go here
                 st.session_state.replay_playing = not st.session_state.get('replay_playing', False)
                 st.rerun()
                 
        start_t = meta['time']
        new_t = st.slider("Scrub Time", 0.0, 200.0, float(start_t))
        if new_t != start_t:
            # Jump logic manual
            engine.scenario_time = new_t # Direct set for scrubbing
            engine.tick_scenario(0) # Update state immediately
            st.rerun()

        # INCIDENT ANALYSIS PANEL
        st.markdown("---")
        st.markdown("### 📋 SYSTEM ANALYSIS")
        
        st.info(f"**CURRENT STATE:** {meta['desc']}")
        
        st.markdown(f"""
        <div style="background: rgba(255, 0, 0, 0.1); border-left: 5px solid #ff4444; padding: 15px; margin-top: 10px;">
            <h4 style="margin-top:0; color: #ff8888;">CAUSE → EFFECT</h4>
            <p style="font-size: 1.1em;">{meta['analysis']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-Play Logic
        if st.session_state.get('replay_playing', False):
            # Placeholder for indicator
            st.caption("▶️ REPLAY ACTIVE")

    st.markdown("---")
    if st.button("⛔ STOP REPLAY & RETURN"):
        engine.unload_scenario()
        st.session_state.replay_playing = False
        navigate_func("incidents")

    # --- AUTO-PLAY LOGIC (Must be last) ---
    if st.session_state.get('replay_playing', False):
        time.sleep(0.5)
        # Advance scenario time
        engine.tick(2.0)
        st.rerun()
