import streamlit as st
import time
import base64
from logic.engine import ReactorEngine
from logic.visuals import VisualGenerator

def show():
    # Ensure Engine
    if 'engine' not in st.session_state:
        st.session_state.engine = ReactorEngine()
    
    engine = st.session_state.engine
    # God Mode always focuses on Unit A logic but controls the universe
    u_id = "A"
    unit = engine.units[u_id]
    data = unit.get_full_state()
    telemetry = data['telemetry']
    config = unit.config
    
    # --- GLOBAL HEADER ---
    st.markdown("""
    <div style="text-align:center; padding:10px; border-bottom:1px solid #e74c3c; background: #2c0b0e;">
        <h2 style="color:#e74c3c; margin:0;">👁️ GOD MODE: SYSTEMS AUTHORITY</h2>
        <div style="color:#888; font-size:0.8em; letter-spacing:2px;">OMNISCIENT CONTROL ENABLED</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-Run Toggle (Top Side)
    col_t_1, col_t_2 = st.columns([4, 1])
    with col_t_2:
        god_autorun = st.toggle("GOD TIME (Auto-Run)", value=st.session_state.get("auto_run", False))
    
    # --- LAYOUT: 3 COLUMNS (LAWS | TRUTH | CONSEQUENCES) ---
    c_laws, c_truth, c_cons = st.columns([1.2, 1.5, 1.3])
    
    with c_laws:
        st.markdown("### 📜 SYSTEM LAWS")
        st.info("Directly manipulate physical constants.")
        
        # A. PHYSICS AUTHORITY
        st.markdown("**PHYSICS**")
        new_resp = st.slider("Responsiveness (Time Const)", 0.1, 3.0, config.responsiveness, 0.1)
        new_chaos = st.slider("Non-Linearity (Chaos)", 0.0, 1.0, config.non_linearity, 0.1)
        new_coupling = st.slider("Subsystem Coupling", 0.0, 1.0, config.coupling_strength, 0.1)
        
        st.markdown("---")
        # B. SAFETY BIAS
        st.markdown("**PHILOSOPHY**")
        new_safety = st.slider("Safety Bias (Conservative ↔ Forgiving)", 0.0, 1.0, config.safety_bias, 0.1)
        new_feedback = st.slider("Neg. Feedback Dominance", 0.0, 2.0, config.feedback_strength, 0.1)
        
        # Apply Changes
        if (new_resp != config.responsiveness or new_chaos != config.non_linearity or 
            new_coupling != config.coupling_strength or new_safety != config.safety_bias or
            new_feedback != config.feedback_strength):
            
            engine.update_config(u_id, {
                "responsiveness": new_resp,
                "non_linearity": new_chaos,
                "coupling_strength": new_coupling,
                "safety_bias": new_safety,
                "feedback_strength": new_feedback
            })
            st.rerun()

    with c_truth:
        st.markdown("<div style='text-align:center'><b>TRUTH MIRROR</b></div>", unsafe_allow_html=True)
        # Visual Core
        svg = VisualGenerator.get_reactor_svg({
            "temp": telemetry["temp"],
            "flux": telemetry["flux"],
            "rods": data['controls']["rods_pos"],
            "scram": telemetry["scram"],
            "stability_margin": telemetry["stability_margin"]
        })
        b64_svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        
        # Pulse if chaos is high
        pulse_class = "tension-active" if config.non_linearity > 0.5 or telemetry["stability_margin"] < 40 else ""
        
        st.markdown(f"""
        <div class="reactor-container {pulse_class}" style="border-color:#e74c3c;">
            <img src="data:image/svg+xml;base64,{b64_svg}" style="width: 100%; height: 400px;">
        </div>
        """, unsafe_allow_html=True)
        
        # Disaster Injection
        st.markdown("### ⚡ DISASTER AUTHORITY")
        c_d1, c_d2, c_d3 = st.columns(3)
        if c_d1.button("EARTHQUAKE"):
            engine.inject_disturbance(u_id, "EARTHQUAKE")
            st.toast("Injecting Seismic Event...", icon="🌋")
        if c_d2.button("FLOOD"):
            engine.inject_disturbance(u_id, "FLOOD")
            st.toast("Cooling Systems Flooded...", icon="🌊")
        if c_d3.button("NORMALIZE"):
            engine.inject_disturbance(u_id, "RESET")
            st.toast("Restoring Standard Reality...", icon="✨")

    with c_cons:
        st.markdown("### 📉 CONSEQUENCES")
        
        # Derived Metrics Visuals
        def meta_metric(label, val, range_bad=(0.2, 0.8), inverse=False):
            # range_bad: below 0.2 is bad, above 0.8 is good? No, let's simplify.
            # val is 0.0 to 1.0.
            # standard: 1.0 is GREEN, 0.0 is RED
            color = "#2ecc71"
            if val < 0.8: color = "#f1c40f"
            if val < 0.4: color = "#e74c3c"
            
            if inverse: # 1.0 is BAD (Red)
                color = "#2ecc71"
                if val > 0.2: color = "#f1c40f"
                if val > 0.6: color = "#e74c3c"
            
            st.markdown(f"""
            <div style="margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; color:#aaa; font-size:0.8em;">
                    <span>{label}</span>
                    <span style="color:{color}; font-weight:bold;">{val:.2f}</span>
                </div>
                <div style="background:#333; height:6px; border-radius:3px; overflow:hidden;">
                    <div style="background:{color}; width:{val*100}%; height:100%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        meta_metric("Control Quality Index", telemetry.get("control_quality", 1.0))
        meta_metric("Stability Elasticity", telemetry["stability_margin"]/100.0)
        meta_metric("Escalation Momentum", telemetry.get("escalation_momentum", 0.0), inverse=True)
        meta_metric("Irreversibility Score", telemetry.get("irreversibility_score", 0.0), inverse=True)
        
        st.markdown("---")
        st.markdown("**GLOBAL STATE**")
        st.metric("Risk Accumulation", f"{telemetry.get('risk_accumulated', 0):.1f}", delta="Cumulative")

    # CAUSE TRACE
    st.markdown("---")
    st.markdown("**🔗 CAUSAL CHAIN TRACE**")
    # Dynamic text based on config
    chain = []
    if config.responsiveness > 1.2: chain.append("High Sensitivity")
    if config.feedback_strength < 0.8: chain.append("Weak Damping")
    if config.non_linearity > 0.5: chain.append("Chaotic Dynamics")
    if telemetry['flux'] > 1.0: chain.append("Power Excursion")
    if telemetry['temp'] > 600: chain.append("Thermal Stress")
    
    if not chain: chain = ["System Nominal", "Stable Equilibrium"]
    
    trace_html = " <span style='color:#666'>➜</span> ".join([f"<span style='border:1px solid #444; padding:2px 8px; border-radius:4px; color:#ddd;'>{c}</span>" for c in chain])
    st.markdown(trace_html, unsafe_allow_html=True)
    
    # AUTO RUN logic needed here too
    # AUTO RUN logic (Using top toggle state)
    if god_autorun:
         time.sleep(0.5)
         engine.tick(1.0)
         st.rerun()
