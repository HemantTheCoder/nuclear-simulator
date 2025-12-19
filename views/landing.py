import streamlit as st

def show(navigate_func):
    # CSS for the landing page specifically
    st.markdown("""
    <style>
    .nuclear-title { font-size: 3.5em; font-weight: 800; background: -webkit-linear-gradient(#ffcc00, #ff6600); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 2px; }
    .nuclear-subtitle { font-size: 1.2em; color: #aaa; font-family: 'Courier New', monospace; margin-bottom: 40px; border-left: 3px solid #ffcc00; padding-left: 15px; }
    .safety-panel { background: rgba(255, 204, 0, 0.1); border: 1px solid #ffcc00; padding: 20px; border-radius: 5px; margin-top: 30px; }
    .safety-header { color: #ffcc00; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    </style>
    """, unsafe_allow_html=True)
    
    # 1. LANDING SCREEN
    col_spacer, col_content, col_spacer2 = st.columns([1, 2, 1])
    
    with col_content:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True) # Spacer
        st.markdown("<div class='nuclear-title'>Nuclear Reactor<br>Systems Simulator</div>", unsafe_allow_html=True)
        st.markdown("<div class='nuclear-subtitle'>Understanding control, stability, and safety in complex energy systems.<br>SYSTEMS ENGINEERING • OPERATOR TRAINING • SAFETY ANALYSIS</div>", unsafe_allow_html=True)
        
        # 2. VISUAL (Abstract Reactor)
        st.markdown("""
        <div style="display: flex; justify-content: center; margin: 30px 0;">
            <svg width="200" height="200" viewBox="0 0 200 200">
                <circle cx="100" cy="100" r="80" stroke="#333" stroke-width="2" fill="none" />
                <circle cx="100" cy="100" r="60" stroke="#444" stroke-width="2" fill="none" stroke-dasharray="10 5" />
                <circle cx="100" cy="100" r="40" stroke="#ffcc00" stroke-width="4" fill="none">
                    <animate attributeName="opacity" values="0.5;1;0.5" duration="3s" repeatCount="indefinite" />
                </circle>
                <circle cx="100" cy="100" r="10" fill="#ff6600">
                    <animate attributeName="r" values="10;15;10" duration="2s" repeatCount="indefinite" />
                </circle>
                <path d="M100 20 L100 180 M20 100 L180 100" stroke="rgba(255,204,0,0.2)" stroke-width="1" />
            </svg>
        </div>
        """, unsafe_allow_html=True)

        # 3. MANDATORY CONTEXT PANEL
        st.markdown("""
        <div class="safety-panel">
            <div class="safety-header">⚠️ SIMULATION CONTEXT & SAFETY BRIEF</div>
            <ul style="color: #ddd; font-size: 0.9em; line-height: 1.6;">
                <li><strong>Conceptual Simulator:</strong> This platform models reactor physics principles (reactivity, thermal-hydraulics) but simplifies operational procedures.</li>
                <li><strong>Normalized Values:</strong> All metrics (Power, Flux, Temp) are normalized for educational clarity.</li>
                <li><strong>Safety Focus:</strong> This simulator explains system behavior and safety lessons. It does not teach reactor operation.</li>
                <li><strong>"You are learning how complex systems behave."</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.checkbox("I acknowledge that this is an educational simulation.", value=False):
            if st.button("ENTER CONTROL ROOM ☢️", type="primary", use_container_width=True):
                navigate_func('simulator')
            
        st.markdown("<div style='text-align:center; margin-top:20px; color:#444; font-size: 0.8em;'>v1.0-NUC | Systems Engineering Div</div>", unsafe_allow_html=True)
