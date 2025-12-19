class VisualGenerator:
    @staticmethod
    def get_color_from_temp(temp):
        """Returns a hex color based on temperature (Celsius)."""
        # 300C (Blue/Normal) -> 800C (Red/Meltdown) -> 2000C (White/Vapor)
        if temp < 300: return "#3498db" # Cool Blue
        if temp < 400: return "#2ecc71" # Nominal Green
        if temp < 600: return "#f1c40f" # Warning Yellow
        if temp < 1000: return "#e74c3c" # Critical Red
        return "#ecf0f1" # Meltdown White

    @staticmethod
    def get_reactor_svg(telemetry):
        temp = telemetry.get("temp", 300)
        flux = telemetry.get("flux", 0.0)
        rods_pos = telemetry.get("rods", 50.0)
        scram = telemetry.get("scram", False)
        stability = telemetry.get("stability_margin", 100.0) # 0-100
        
        core_color = VisualGenerator.get_color_from_temp(temp)
        glow_opacity = min(1.0, flux * 1.5)
        rod_height = 20 + (rods_pos / 100.0) * 160 # 20px (Out) to 180px (In)
        
        # JITTER CALCULATION
        # Stability < 50 starts minor jitter. Stability < 20 is severe.
        jitter_anim = ""
        if stability < 60:
            intensity = (60 - stability) / 20.0 # 0 to 3px
            jitter_anim = f"""
            <animateTransform attributeName="transform" type="translate" values="0,0; {intensity},{intensity}; -{intensity},0; 0,-{intensity}; 0,0" dur="0.1s" repeatCount="indefinite" />
            """
        
        # Particle Speed (Flux) - Lower duration = Faster
        # flux 0.0 -> dur 20s (static)
        # flux 1.0 -> dur 0.5s (fast)
        anim_dur = max(0.2, 2.0 - (flux * 1.8))
        
        # Scram Overlay
        scram_overlay = ""
        if scram:
            scram_overlay = """
            <rect x="50" y="20" width="200" height="360" rx="20" fill="url(#scramGradient)" opacity="0.4">
                <animate attributeName="opacity" values="0.4;0.2;0.4" dur="2s" repeatCount="indefinite" />
            </rect>
            <text x="150" y="200" font-family="monospace" font-size="24" fill="red" text-anchor="middle" font-weight="bold" opacity="0.8">SCRAM ENGAGED</text>
            """

        svg = f"""
        <svg width="300" height="400" viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="coolantGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" stop-color="#2c3e50" />
                    <stop offset="100%" stop-color="#34495e" />
                </linearGradient>
                <radialGradient id="cerenkovInfo" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                    <stop offset="0%" stop-color="#00ffff" stop-opacity="{glow_opacity}" />
                    <stop offset="100%" stop-color="#0000ff" stop-opacity="0" />
                </radialGradient>
                <linearGradient id="scramGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#ff0000" stop-opacity="0.5" />
                    <stop offset="100%" stop-color="#550000" stop-opacity="0.8" />
                </linearGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            
            <!-- Global Stability Jitter Group -->
            <g>
                {jitter_anim}
            
            <!-- Vessel Background -->
            <rect x="50" y="20" width="200" height="360" rx="20" ry="20" fill="url(#coolantGrad)" stroke="#7f8c8d" stroke-width="4" />
            
            <!-- Fuel Assembly Area (Heat Source) -->
            <rect x="70" y="100" width="160" height="200" rx="5" fill="{core_color}" opacity="0.4" filter="url(#glow)">
                 <!-- Thermal Pulse Animation -->
                 <animate attributeName="opacity" values="0.4;0.6;0.4" dur="{anim_dur*2}s" repeatCount="indefinite" />
            </rect>
            
            <!-- Flux (Cerenkov Glow) -->
            <rect x="70" y="100" width="160" height="200" rx="5" fill="url(#cerenkovInfo)">
                 <animate attributeName="opacity" values="{glow_opacity};{max(0, glow_opacity-0.2)};{glow_opacity}" dur="0.1s" repeatCount="indefinite" />
            </rect>

            <!-- Bubbles / Particles Visualization (Neutron Flux) -->
            <g opacity="{min(1.0, flux * 2.0)}">
                <circle cx="100" cy="300" r="3" fill="rgba(255,255,255,0.6)">
                    <animate attributeName="cy" from="300" to="100" dur="{anim_dur}s" repeatCount="indefinite" />
                    <animate attributeName="cx" values="100;110;100" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="150" cy="300" r="4" fill="rgba(255,255,255,0.6)">
                    <animate attributeName="cy" from="320" to="100" dur="{anim_dur * 1.2}s" repeatCount="indefinite" />
                </circle>
                <circle cx="200" cy="300" r="2" fill="rgba(255,255,255,0.6)">
                    <animate attributeName="cy" from="310" to="100" dur="{anim_dur * 0.8}s" repeatCount="indefinite" />
                    <animate attributeName="cx" values="200;190;200" dur="2s" repeatCount="indefinite" />
                </circle>
                 <circle cx="125" cy="300" r="3" fill="rgba(255,255,255,0.4)">
                    <animate attributeName="cy" from="330" to="100" dur="{anim_dur * 0.9}s" repeatCount="indefinite" />
                </circle>
                <circle cx="175" cy="300" r="3" fill="rgba(255,255,255,0.4)">
                    <animate attributeName="cy" from="340" to="100" dur="{anim_dur * 1.1}s" repeatCount="indefinite" />
                </circle>
            </g>

            <!-- Control Rods (Animated Position) -->
            <!-- Rod 1 -->
            <rect x="90" y="20" width="20" height="{rod_height}" fill="#95a5a6" stroke="#bdc3c7" stroke-width="1">
                 <animate attributeName="height" to="{rod_height}" dur="0.5s" fill="freeze" />
            </rect>
            <!-- Rod 2 (Center) -->
            <rect x="140" y="20" width="20" height="{rod_height}" fill="#95a5a6" stroke="#bdc3c7" stroke-width="1">
                 <animate attributeName="height" to="{rod_height}" dur="0.5s" fill="freeze" />
            </rect>
            <!-- Rod 3 -->
            <rect x="190" y="20" width="20" height="{rod_height}" fill="#95a5a6" stroke="#bdc3c7" stroke-width="1">
                 <animate attributeName="height" to="{rod_height}" dur="0.5s" fill="freeze" />
            </rect>

            <!-- Safety Overlay if SCRAM -->
            {scram_overlay}
            
            <!-- Flow Indicators -->
             <path d="M 60 300 Q 40 350 150 370 Q 260 350 240 300" stroke="#3498db" stroke-width="2" fill="none" opacity="0.5" stroke-dasharray="5,5">
                <animate attributeName="stroke-dashoffset" from="100" to="0" dur="2s" repeatCount="indefinite" />
             </path>


            <!-- End Global Jitter -->
            </g>
        </svg>
        """
        return svg
