import streamlit as st
from logic.scenarios.historical import SCENARIOS

def show(navigate_func):
    st.markdown("## 🏛 HISTORICAL INCIDENT LIBRARY")
    st.markdown("Select a major event to analyze its timeline and failure cascade.")
    
    # 1. HEADER / CONTEXT
    st.info("These reconstructions are educational simplifications focused on system dynamics, not operational procedures.")
    
    # 2. INCIDENT GRID
    cols = st.columns(3)
    
    # Chernobyl
    with cols[0]:
        st.markdown("### ☢️ Chernobyl Unit 4")
        st.caption("1986 | RBMK-1000 | Ukraine")
        st.markdown("**The Disaster:** A safety test gone wrong leads to a prompt critical excursion and steam explosion.")
        st.markdown("*Key Lessons: Positive Scram Effect, Safety Culture, Design Flaws.*")
        if st.button("REPLAY INCIDENT", key="btn_chernobyl", type="primary", use_container_width=True):
            st.session_state.engine.load_scenario("chernobyl")
            navigate_func("replay")
            
    # TMI
    with cols[1]:
        st.markdown("### ⚠️ Three Mile Island")
        st.caption("1979 | PWR | USA")
        st.markdown("**The Accident:** A stuck relief valve and confusing UI lead operators to inadvertently drain the core.")
        st.markdown("*Key Lessons: Human Factors, Instrumentation Ambiguity, LOCA.*")
        if st.button("REPLAY INCIDENT", key="btn_tmi", type="primary", use_container_width=True):
            st.session_state.engine.load_scenario("tmi")
            navigate_func("replay")

    # Fukushima
    with cols[2]:
        st.markdown("### 🌊 Fukushima Daiichi")
        st.caption("2011 | BWR | Japan")
        st.markdown("**The Station Blackout:** A massive tsunami floods diesel generators, disabling all cooling systems.")
        st.markdown("*Key Lessons: External Hazards, Defense in Depth, Hydrogen Venting.*")
        if st.button("REPLAY INCIDENT", key="btn_fukushima", type="primary", use_container_width=True):
            st.session_state.engine.load_scenario("fukushima")
            navigate_func("replay")
            
    st.markdown("---")
    if st.button("⬅ BACK TO CONTROL ROOM"):
        navigate_func("simulator")
