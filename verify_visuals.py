from logic.visuals import VisualGenerator

def test_visuals():
    print("Testing Visual Generator...")
    
    # PWR Test
    ctx_pwr = {
        "type": "PWR",
        "temp": 300,
        "flux": 0.5,
        "rods_pos": 50,
        "flow_rate_core": 80,
        "pressure": 150,
        "pressurizer_heaters": True,
        "pressurizer_sprays": False
    }
    svg_pwr = VisualGenerator.get_reactor_svg(ctx_pwr)
    assert "<svg" in svg_pwr
    assert "animate" in svg_pwr # Check for animation
    print("PWR SVG Generated OK")

    # BWR Test
    ctx_bwr = {
        "type": "BWR",
        "temp": 280,
        "flux": 0.8,
        "rods_pos": 20,
        "void_fraction": 0.05,
        "msiv_open": False,
        "turbine_bypass": 50
    }
    svg_bwr = VisualGenerator.get_reactor_svg(ctx_bwr)
    assert "MSIV" in svg_bwr
    assert "fill=\"#e74c3c\"" in svg_bwr # Red valve
    print("BWR SVG Generated OK")

    # RBMK Test
    ctx_rbmk = {
        "type": "RBMK",
        "temp": 350,
        "flux": 1.0,
        "rods_pos": 80,
        "flow_rate_core": 100
    }
    svg_rbmk = VisualGenerator.get_reactor_svg(ctx_rbmk)
    assert "RBMK-1000" in svg_rbmk
    assert "fill=\"#e67e22\"" in svg_rbmk # Tip color
    print("RBMK SVG Generated OK")

if __name__ == "__main__":
    try:
        test_visuals()
        print("ALL VISUALS PASSED")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")
