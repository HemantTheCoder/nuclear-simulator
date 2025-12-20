import pandas as pd
import io
import os
import streamlit as st
from fpdf import FPDF
import plotly.graph_objects as go
from datetime import datetime

class ReportGenerator:
    """
    Generates multi-page PDF reports for reactor sessions or historical reconstructions.
    """
    
    @staticmethod
    def generate_pdf(unit, session_history):
        """
        Compiles telemetry, logs, and graphs into a PDF.
        Returns a byte-stream.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # --- HEADER ---
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(220, 50, 50) 
        pdf.cell(0, 15, "NUCLEAR ACCIDENT ANALYSIS REPORT", ln=1, align='C')
        
        pdf.set_font("helvetica", "I", 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
        
        # Horizontal Line
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y()+5, 200, pdf.get_y()+5)
        pdf.ln(15)
        
        # --- UNIT IDENTITY ---
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 0, 0)
        # Center the Unit Info Box
        pdf.cell(0, 10, f"Reactor Unit: {str(unit.name)}", ln=1, align='C')
        
        pdf.set_font("helvetica", "", 12)
        health = unit.telemetry.get('health', 100.0)
        status_str = 'DESTROYED' if health <=0 else 'OPERATIONAL'
        
        # Simple table-like structure for metrics
        x_start = 60
        pdf.set_x(x_start)
        pdf.cell(50, 8, "Final Status:", border=0)
        pdf.cell(0, 8, status_str, ln=1)
        
        pdf.set_x(x_start)
        pdf.cell(50, 8, "Final Temperature:", border=0)
        pdf.cell(0, 8, f"{unit.telemetry.get('temp', 0):.1f} C", ln=1)
        
        pdf.set_x(x_start)
        pdf.cell(50, 8, "Radiation Released:", border=0)
        pdf.cell(0, 8, f"{unit.telemetry.get('radiation_released', 0):.2f} Sv", ln=1)
        pdf.ln(5)

        # --- SYSTEM SPECIFICATIONS ---
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "SYSTEM SPECIFICATIONS", ln=1)
        pdf.set_font("helvetica", "", 10)
        c = unit.config
        
        pdf.set_x(20)
        pdf.cell(60, 6, "Reactor Type:", border=1)
        pdf.cell(60, 6, f"{unit.type.value}", border=1, ln=1)
        
        pdf.set_x(20)
        pdf.cell(60, 6, "Max Thermal Power:", border=1)
        pdf.cell(60, 6, "3200 MWth", border=1, ln=1)
        
        pdf.set_x(20)
        pdf.cell(60, 6, "Void Coefficient:", border=1)
        pdf.cell(60, 6, f"{c.void_coefficient:+.3f}", border=1, ln=1)
        
        pdf.set_x(20)
        pdf.cell(60, 6, "Doppler Coefficient:", border=1)
        pdf.cell(60, 6, f"{c.doppler_coefficient:+.3f}", border=1, ln=1)
        pdf.ln(5)

        # --- SAFETY SYSTEMS ---
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "SYSTEM CONFIGURATION & SAFETY", ln=1)
        pdf.set_font("courier", "", 10)
        
        s_scram = "ACTIVE" if unit.telemetry.get("scram") else "READY"
        s_eccs = "INJECTING" if unit.control_state.get("eccs_active") else "STANDBY"
        s_cont = f"{unit.telemetry.get('containment_integrity', 100):.1f}%"
        s_msiv = "CLOSED (ISOLATED)" if not unit.control_state.get("msiv_open", True) else "OPEN (NORMAL)"
        s_auto = "ENGAGED" if unit.control_state.get("auto_rod_control", False) else "MANUAL"
        s_load = f"{unit.control_state.get('turbine_load_mw', 1000):.0f} MW"
        
        pdf.set_x(20)
        pdf.cell(0, 6, f"[SCRAM SYSTEM] ....... {s_scram}", ln=1)
        pdf.set_x(20)
        pdf.cell(0, 6, f"[ECCS PUMPS] ......... {s_eccs}", ln=1)
        pdf.set_x(20)
        pdf.cell(0, 6, f"[CONTAINMENT] ........ {s_cont}", ln=1)
        pdf.set_x(20)
        pdf.cell(0, 6, f"[MSIV STATUS] ........ {s_msiv}", ln=1)
        pdf.set_x(20)
        pdf.cell(0, 6, f"[ROD CONTROL] ........ {s_auto}", ln=1)
        pdf.set_x(20)
        pdf.cell(0, 6, f"[GRID DEMAND] ........ {s_load}", ln=1)
        pdf.ln(10)
        
        # --- CHAIN OF EVENTS ---
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "CHAIN OF EVENTS", ln=1)
        pdf.set_font("courier", "", 10)
        
        for event in unit.event_log:
            time_str = f"T+{event['time']:.1f}s"
            msg = str(event['event']).encode('latin-1', 'ignore').decode('latin-1')
            
            # Use X position for the message to avoid multi_cell width calculation issues
            curr_y = pdf.get_y()
            pdf.cell(25, 6, time_str, border=0)
            
            # Calculate width remaining
            page_width = pdf.w - pdf.l_margin - pdf.r_margin
            msg_width = page_width - 35
            
            pdf.set_x(35) # Move to fixed X for the message
            pdf.multi_cell(msg_width, 6, msg)
            
            # Ensure next line starts after the multi_cell block
            # If multi_cell didn't wrap, get_y might not have advanced much if we forced set_x back? 
            # FPDF's multi_cell advances Y.
            # But we need to make sure we don't overwrite if manual Y management needed.
            # Actually standard multi_cell behavior is fine, but we need to ensure the TIME column checks alignment
            # For list items, simple flow is usually okay.
            pass
        
        # --- ANALYSIS (From Post-Mortem) ---
        if unit.post_mortem_report:
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "POST-MORTEM ANALYSIS", ln=1)
            pdf.set_font("helvetica", "", 12)
            expl = str(unit.post_mortem_report['explanation']).encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 8, expl)
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Prevention Steps:", ln=1)
            pdf.set_font("helvetica", "", 11)
            pdf.set_font("helvetica", "", 11)
            
            # Robust iteration (handle string or list)
            tips = unit.post_mortem_report['prevention']
            if isinstance(tips, str):
                tips = [tips]
                
            for tip in tips:
                pdf.set_x(20) # Indent
                pdf.cell(5, 8, "-", align='R')
                
                # Handling multi-line tips
                t_msg = str(tip).encode('latin-1', 'ignore').decode('latin-1')
                
                # Calculate remaining width
                page_width = pdf.w - pdf.l_margin - pdf.r_margin
                curr_x = pdf.get_x()
                width_avail = page_width - curr_x
                
                pdf.multi_cell(width_avail, 8, t_msg)

        # --- GRAPHS ---
        if session_history:
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "TELEMETRY TRENDS", ln=1)
            
            df = pd.DataFrame(session_history)
            
            try:
                # Use cached generation to prevent Kaleido resource leaks
                img_bytes = ReportGenerator._create_trend_image(df)
                
                # FPDF 2.0+ handles bytes directly if passed as a stream-like object or sometimes directly
                # It's safer to wrap in BytesIO with a name property if possible, or just pass bytes if FPDF supports it.
                # Assuming previous code worked, we keep it. But let's be explicit with a temp buffer if needed.
                # Actually, FPDF often needs a stream for bytes.
                if img_bytes:
                    import io
                    # Create a BytesIO object with a name attribute so FPDF knows it's a PNG
                    img_stream = io.BytesIO(img_bytes)
                    img_stream.name = 'temp_trend.png' 
                    pdf.image(img_stream, x=10, y=30, w=190)
            except Exception as e:
                pdf.set_font("helvetica", "I", 10)
                pdf.cell(0, 10, f"(Graph generation skipped: {str(e)})", ln=1)

            # --- REACTIVITY BALANCE GRAPH ---
            try:
                # Use cached generation 
                r_img_bytes = ReportGenerator._create_reactivity_image(df)
                
                if r_img_bytes:
                    pdf.add_page()
                    pdf.set_font("helvetica", "B", 16)
                    pdf.cell(0, 10, "REACTIVITY BALANCE", ln=1)
                    pdf.set_font("helvetica", "", 12)
                    pdf.multi_cell(0, 6, "Detailed breakdown of reactivity components (Control Rods, Void, Doppler, Xenon) contributing to the net reactivity state.")
                    
                    import io
                    r_img_stream = io.BytesIO(r_img_bytes)
                    r_img_stream.name = 'temp_reactivity.png' 
                    pdf.image(r_img_stream, x=10, y=50, w=190)
            except Exception as e:
                    pdf.set_font("helvetica", "I", 10)
                    pdf.cell(0, 10, f"(Reactivity graph skipped: {str(e)})", ln=1)

        # --- GLOSSARY ---
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "TECHNICAL REFERENCE & GLOSSARY", ln=1)
        pdf.set_font("helvetica", "", 10)
        
        glossary = {
            "Departure from Nucleate Boiling Ratio (DNBR)": 
                "A measure of the thermal safety margin. It is the ratio of the Critical Heat Flux (heat level where bubbles form a blanket, blocking cooling) to the actual heat flux. A DNBR < 1.3 implies a high risk of fuel rod damage and melting.",
            
            "Void Coefficient of Reactivity": 
                "Determines how reactor power changes when water boils into steam (voids). Negative = Self-stabilizing (Power drops as boiling increases). Positive = Instability (Power rises as boiling increases, leading to runaway).",
            
            "Doppler Broadening (Doppler Coefficient)": 
                "A negative feedback mechanism where heating up the fuel makes it absorb more neutrons (due to atomic vibration), naturally dampening the nuclear reaction. This is a key inherent safety feature.",
            
            "Xenon Poisoning (Xenon-135)": 
                "A fission product that absorbs neutrons, 'poisoning' the reaction. It builds up after shutdown (Xenon Pit), preventing restart for ~24 hours. Attempting to override it by pulling control rods is dangerous.",
                
            "Tip Effect (Positive Scram)":
                "A design flaw in RBMK reactors where control rods have graphite displacers at the tips. When inserting rods to shut down, the graphite tip initially adds reactivity, potentially causing a power spike before shutdown.",
                
            "Main Steam Isolation Valve (MSIV)":
                "Safety valves that isolate the reactor from the turbine hall. Closing them while the reactor is at power causes a rapid pressure spike, necessitating the use of bypass valves or safety relief valves."
        }
        
        for term, desc in glossary.items():
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 6, term, ln=1)
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 5, desc)

        # Output to buffer (Return bytes)
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, (bytes, bytearray)):
            return bytes(pdf_bytes)
        return pdf_bytes.encode('latin-1')

    @staticmethod
    @st.cache_data(show_spinner=False, ttl=60)
    def _create_trend_image(df):
        """Creates a static graph image for PDF inclusion."""
        if df.empty: return None
        fig = go.Figure()
        
        # Color palette
        colors = {"power_mw": "#1f77b4", "temp": "#d62728", "pressure": "#ff7f0e"}
        
        for col in ["power_mw", "temp", "pressure"]:
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['time_seconds'] if 'time_seconds' in df.columns else df.index, 
                    y=df[col], 
                    name=col.upper(),
                    line=dict(color=colors.get(col, "#888888"), width=2)
                ))
        
        fig.update_layout(
            template="plotly_dark",
            title="Session Telemetry",
            xaxis_title="Time (s)",
            yaxis_title="Value",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400,
            width=800
        )
        
        # Return as bytes
        # engine='kaleido' is required for static image export
        return fig.to_image(format="png", engine="kaleido")

    @staticmethod
    @st.cache_data(show_spinner=False, ttl=60)
    def _create_reactivity_image(df):
        """Creates a detailed reactivity balance graph."""
        if df.empty or 'rho_void' not in df.columns: return None
        fig = go.Figure()
        
        comps = ["rho_void", "rho_doppler", "rho_xenon", "rho_rods"]
        colors = {"rho_void": "#e74c3c", "rho_doppler": "#3498db", "rho_xenon": "#9b59b6", "rho_rods": "#95a5a6"}
        
        for c in comps:
             if c in df.columns:
                 fig.add_trace(go.Scatter(
                    x=df['time_seconds'], y=df[c], name=c.replace("rho_", "").title(),
                    line=dict(color=colors.get(c, "#fff"), width=2)
                ))
        
        if 'reactivity' in df.columns:
            fig.add_trace(go.Scatter(x=df['time_seconds'], y=df['reactivity'], name="NET TOTAL", line=dict(color="white", width=4, dash='dot')))

        fig.update_layout(
            template="plotly_dark", title="Reactivity Balance (PCM)",
            xaxis_title="Time (s)", yaxis_title="Reactivity (pcm)",
            margin=dict(l=20, r=20, t=40, b=20), height=400, width=800
        )
        return fig.to_image(format="png", engine="kaleido")
