import streamlit as st
import importlib
from logic.engine import ReactorEngine

# Page Config
st.set_page_config(
    page_title="Nuclear Reactor Systems Simulator",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

if 'engine' not in st.session_state:
    st.session_state.engine = ReactorEngine()
    st.session_state.active_unit_id = "A" # Default for take-control

# Navigation Logic
def navigate_to(page):
    st.session_state.page = page
    # Clear temporary reconstruction modes when navigating away from Incidents/Archives
    if page != 'incidents':
        st.session_state.mode = None
    st.rerun()

# Module Imports
views_landing = importlib.import_module("views.landing")
views_simulator = importlib.import_module("views.simulator")
views_incidents = importlib.import_module("views.incidents")
views_replay = importlib.import_module("views.replay")
views_analytics = importlib.import_module("views.analytics")

# Logic for SIDEBAR (Global Navigation)
with st.sidebar:
    st.title("☢️ CONTROL NET")
    st.markdown("""
        <div style="font-size: 0.85em; color: #aaa; margin-bottom: 20px; margin-top: -15px;">
            By <a href="https://www.linkedin.com/in/hemantkumar2430/" target="_blank" style="color: #ffcc00; text-decoration: none;">Hemant Kumar</a> & 
            <a href="https://www.linkedin.com/in/jaidev-joya-0a5690284/" target="_blank" style="color: #ffcc00; text-decoration: none;">Jaidev Joya</a>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Control Room", use_container_width=True): navigate_to("simulator")
    if st.button("Incident Library", use_container_width=True): navigate_to("incidents")
    if st.button("Analytics & Logs", use_container_width=True): navigate_to("analytics")
    
    st.markdown("---")
    st.caption("Active Session: " + st.session_state.page.upper())
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size: 0.8em; color: #666; border-top: 1px solid #333; padding-top: 20px;">
            Made by <br>
            <a href="https://www.linkedin.com/in/hemantkumar2430/" target="_blank" style="color: #ffcc00; text-decoration: none;">Hemant Kumar</a> & 
            <a href="https://www.linkedin.com/in/jaidev-joya-0a5690284/" target="_blank" style="color: #ffcc00; text-decoration: none;">Jaidev Joya</a>
        </div>
    """, unsafe_allow_html=True)

# Main Routing
if st.session_state.page == 'landing':
    views_landing.show(navigate_to)
elif st.session_state.page == 'simulator':
    views_simulator.show(navigate_to)
elif st.session_state.page == 'incidents':
    views_incidents.show(navigate_to)
elif st.session_state.page == 'replay':
    views_replay.show(navigate_to)
elif st.session_state.page == 'analytics':
    views_analytics.show(navigate_to)
