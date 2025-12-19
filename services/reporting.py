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
        pdf.ln(10)
        
        # --- UNIT IDENTITY ---
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Reactor Unit: {str(unit.name)}", ln=1)
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 8, f"Final Status: {'DESTROYED' if unit.telemetry['health'] <=0 else 'OPERATIONAL'}", ln=1)
        pdf.cell(0, 8, f"Final Temperature: {unit.telemetry['temp']:.1f} C", ln=1)
        pdf.cell(0, 8, f"Radiation Released: {unit.telemetry['radiation_released']:.2f} Sv", ln=1)
        pdf.ln(10)
        
        # --- CHAIN OF EVENTS ---
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "CHAIN OF EVENTS", ln=1)
        pdf.set_font("courier", "", 10)
        
        for event in unit.event_log:
            time_str = f"T+{event['time']:.1f}s"
            msg = str(event['event']).encode('latin-1', 'ignore').decode('latin-1') # Sanitize
            pdf.cell(25, 6, time_str, border=0)
            pdf.multi_cell(0, 6, msg)
            
        pdf.ln(10)
        
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
            for tip in unit.post_mortem_report['prevention']:
                pdf.cell(10, 8, "-", align='R')
                t_msg = str(tip).encode('latin-1', 'ignore').decode('latin-1')
                pdf.cell(0, 8, t_msg, ln=1)

        # --- GRAPHS ---
        if session_history:
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "TELEMETRY TRENDS", ln=1)
            
            df = pd.DataFrame(session_history)
            
            try:
                img_bytes = ReportGenerator._create_trend_image(df)
                if img_bytes:
                    pdf.image(img_bytes, x=10, y=30, w=190)
            except Exception as e:
                pdf.set_font("helvetica", "I", 10)
                pdf.cell(0, 10, f"(Graph generation skipped: {str(e)})", ln=1)

        # Output to buffer (Return bytes)
        return pdf.output(dest='S').encode('latin-1')

    @staticmethod
    def _create_trend_image(df):
        """Creates a static graph image for PDF inclusion."""
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
