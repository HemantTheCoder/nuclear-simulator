from logic.engine import ReactorEngine
from services.reporting import ReportGenerator
import os

def test_pdf_gen():
    print("--- TEST: PDF GENERATION ---")
    eng = ReactorEngine()
    unit = eng.units["A"]
    
    # Sim some history and logs
    unit.log_event("TEST EVENT 1")
    unit.telemetry["temp"] = 350.0
    unit._record_history()
    unit.log_event("TEST EVENT 2")
    unit.telemetry["temp"] = 400.0
    unit._record_history()
    
    try:
        # Test 1: Just text
        print("Testing minimal text PDF...")
        pdf = ReportGenerator.generate_pdf(unit, []) 
        print(f"SUCCESS: Text-only PDF generated ({len(pdf)} bytes)")
        
        # Test 2: With history/graphs
        print("Testing PDF with graphs...")
        pdf_with_graphs = ReportGenerator.generate_pdf(unit, unit.history)
        print(f"SUCCESS: Graph PDF generated ({len(pdf_with_graphs)} bytes)")
        
        with open("test_report.pdf", "wb") as f:
            f.write(pdf_with_graphs)
        print("Full report saved to test_report.pdf")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_pdf_gen()
