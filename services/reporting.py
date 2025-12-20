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
        pdf.ln(10)
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
