import streamlit as st

def show(navigate_func):
    # CSS for the landing page specifically
    st.markdown("""
    <style>
    .nuclear-title { font-size: 4em; font-weight: 900; background: -webkit-linear-gradient(#ffcc00, #ff6600); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; text-transform: uppercase; letter-spacing: -1px; line-height: 1; }
    .nuclear-subtitle { font-size: 1.1em; color: #888; font-family: 'Inter', sans-serif; margin-bottom: 40px; letter-spacing: 2px; }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 12px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: #ffcc00;
        background: rgba(255, 204, 0, 0.05);
        transform: translateY(-5px);
    }
    .feature-icon { font-size: 2em; margin-bottom: 15px; }
    .feature-title { color: #fff; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; }
    .feature-desc { color: #aaa; font-size: 0.9em; line-height: 1.5; }

    .safety-panel { 
        background: rgba(255, 204, 0, 0.05); 
        border-left: 4px solid #ffcc00; 
        padding: 20px; 
        margin-top: 40px;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 1. HERO SECTION
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True) 
    
    c_hero_1, c_hero_2 = st.columns([2, 1])
    
    with c_hero_1:
        st.markdown("<div class='nuclear-title'>ATOMCORE<br>CONTROL</div>", unsafe_allow_html=True)
        st.markdown("<div class='nuclear-subtitle'>NEXT-GEN REACTOR PHYSICS & FORENSICS</div>", unsafe_allow_html=True)
        
        st.markdown("""
        Experience the world's most detailed in-browser nuclear reactor simulator. 
        From the stable PWR designs to the volatile physics of the RBMK-1000, 
        master the art of energy management and disaster prevention.
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.checkbox("I acknowledge that this is an educational simulation.", value=False):
            if st.button("INITIALIZE SYSTEMS ☢️", type="primary", use_container_width=True):
                navigate_func('simulator')
    
    with c_hero_2:
        # Abstract Reactor Visual
        st.markdown("""
        <div style="display: flex; justify-content: center;">
            <svg width="250" height="250" viewBox="0 0 200 200">
                <defs>
                    <radialGradient id="ringGrad" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" style="stop-color:#ffcc00; stop-opacity:0.2" />
                        <stop offset="100%" style="stop-color:#ff6600; stop-opacity:0" />
                    </radialGradient>
                </defs>
                <circle cx="100" cy="100" r="90" fill="url(#ringGrad)">
                    <animate attributeName="r" values="80;95;80" duration="4s" repeatCount="indefinite" />
                </circle>
                <circle cx="100" cy="100" r="70" stroke="#333" stroke-width="1" fill="none" />
                <circle cx="100" cy="100" r="50" stroke="#444" stroke-width="1" fill="none" stroke-dasharray="8 4" />
                <circle cx="100" cy="100" r="30" stroke="#ffcc00" stroke-width="3" fill="none">
                    <animate attributeName="stroke-opacity" values="0.3;1;0.3" duration="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="100" cy="100" r="8" fill="#ff6600">
                    <animate attributeName="fill" values="#ff6600;#ffcc00;#ff6600" duration="1s" repeatCount="indefinite" />
                </circle>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. FEATURE GRID
    st.markdown("### PLATFORM CAPABILITIES")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚛️</div>
            <div class="feature-title">Multi-Model Physics</div>
            <div class="feature-desc">
                Simulate PWR, BWR, and RBMK-1000 cores. Each reactor features authentic 
                coefficients, graphite tip effects, and xenon poisoning transients.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with f_col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎞️</div>
            <div class="feature-title">Forensic Replays</div>
            <div class="feature-desc">
                Walk through historical reconstructions of Chernobyl, TMI, and Fukushima. 
                Analyze telemetry second-by-second or 'Take Control' to alter outcomes.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with f_col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Detailed Analytics</div>
            <div class="feature-desc">
                Generate high-fidelity forensic PDF reports summarizing your mission. 
                Includes chain-of-events analysis and technical trend graphs.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. SAFETY BRIEF (Important but pushed down slightly)
    st.markdown("""
    <div class="safety-panel">
        <div style="font-weight: bold; color: #ffcc00; margin-bottom: 5px;">⚠️ OPERATION NOTICE</div>
        <div style="font-size: 0.9em; color: #aaa;">
            This platform is a <b>Conceptual Physics Environment</b>. While it models 1:1 real-time reactivity 
            and thermal-hydraulics, it is designed for <b>Educational Visualization</b> and systems 
            engineering awareness, not actual operator certification.
        </div>
    </div>
    """, unsafe_allow_html=True)
