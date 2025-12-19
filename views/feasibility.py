import streamlit as st

def show(navigate_func):
    st.title("🚀 Can We Make Mars Work?")
    if st.button("⬅ Back to Simulator"):
        navigate_func('simulator')

    st.markdown("""
    ### Engineering The Impossible
    Current simulations show that raw exposure to Mars is fatal. Here are the proposed engineering solutions and their massive costs.
    """)

    # Option 1: Dome
    with st.expander("🏗️ Solution 1: Pressurized Geodesic Domes", expanded=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write("Creating a localized Earth atmosphere inside transparent aluminum-glass structures.")
        with c2:
            st.info("**Feasibility**: High  |  **Cost**: $10B per acre")
            st.progress(80, text="Technology Readiness")

    # Option 2: Underground
    with st.expander("🕳️ Solution 2: Lava Tube Habitats"):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write("Using natural caverns to shield from radiation and temperature swings.")
        with c2:
            st.info("**Feasibility**: Medium  |  **Cost**: $2B per acre")
            st.progress(60, text="Technology Readiness")

    # Option 3: Terraform
    with st.expander("🌍 Solution 3: Planetary Terraforming"):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write("Releasing locked CO2 from poles (Nuclear Thermal) to thicken atmosphere.")
        with c2:
            st.error("**Feasibility**: Near Zero (Current Tech)  |  **Time**: ~1000 Years")
            st.progress(10, text="Technology Readiness")

    st.markdown("### 🏁 Final Verdict")
    st.success("Mars is **not impossible**, but it is **not practical** with current technology without massive nuclear energy inputs and sealed habitats.")
