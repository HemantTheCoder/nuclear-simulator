from logic.engine import ReactorType # Needed for enum matching if we used objects, but here we use string matching from telemetry

class VisualGenerator:
    @staticmethod
    def get_color_from_temp(temp):
        if temp < 300: return "#3498db" 
        if temp < 400: return "#2ecc71" 
        if temp < 600: return "#f1c40f" 
        if temp < 1000: return "#e74c3c" 
        return "#ecf0f1" 

    @staticmethod
    def get_melted_svg(telemetry):
        return """
        <svg width="300" height="400" viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="lavaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#ffcc00" />
                    <stop offset="50%" stop-color="#ff0000" />
                    <stop offset="100%" stop-color="#330000" />
                </linearGradient>
            </defs>
            <rect x="0" y="0" width="300" height="400" fill="#111" />
            
            <!-- Cracks -->
            <path d="M 50 100 L 150 200 L 250 50" stroke="#ff0000" stroke-width="2" fill="none" opacity="0.5" />
            <path d="M 100 300 L 200 250 L 300 350" stroke="#ff0000" stroke-width="2" fill="none" opacity="0.5" />
            
            <!-- Melted Core Pile (Corium) -->
            <path d="M 20 350 Q 150 300 280 350 L 280 400 L 20 400" fill="url(#lavaGrad)" />
            
            <!-- Smoke/Steam -->
            <circle cx="100" cy="300" r="50" fill="#555" opacity="0.5">
                <animate attributeName="cy" from="300" to="0" dur="4s" repeatCount="indefinite" />
            </circle>
            <circle cx="200" cy="320" r="40" fill="#444" opacity="0.6">
                <animate attributeName="cy" from="320" to="0" dur="5s" repeatCount="indefinite" />
            </circle>

            <text x="150" y="200" font-family="monospace" font-size="30" fill="red" text-anchor="middle" font-weight="bold">CORE MELTDOWN</text>
            <text x="150" y="240" font-family="monospace" font-size="16" fill="yellow" text-anchor="middle">CRITICALITY ACCIDENT</text>
        </svg>
        """

    @staticmethod
    def get_reactor_svg(telemetry):
        if telemetry.get("melted", False):
            return VisualGenerator.get_melted_svg(telemetry)

        r_type = telemetry.get("type", "PWR") # Default to PWR
        
        if r_type == "RBMK":
            return VisualGenerator.get_rbmk_svg(telemetry)
        elif r_type == "BWR":
            return VisualGenerator.get_bwr_svg(telemetry)
        else:
            return VisualGenerator.get_pwr_svg(telemetry)

    @staticmethod
    def get_common_defs():
        return """
        <defs>
            <linearGradient id="coolantGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#2c3e50" />
                <stop offset="100%" stop-color="#34495e" />
            </linearGradient>
            <radialGradient id="cerenkovInfo" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <stop offset="0%" stop-color="#00ffff" />
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
        """

    @staticmethod
    def get_pwr_svg(telemetry):
        # PWR: Closed Vessel, Pressurizer on top/side
        temp = telemetry.get("temp", 300)
        flux = telemetry.get("flux", 0.0)
        rods_pos = telemetry.get("rods_pos", 50.0) if "rods_pos" in telemetry else telemetry.get("rods", 50.0)
        
        core_color = VisualGenerator.get_color_from_temp(temp)
        glow_opacity = min(1.0, flux * 1.5)
        rod_height = 20 + (rods_pos / 100.0) * 160 
        
        return f"""
        <svg width="300" height="400" viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
            {VisualGenerator.get_common_defs()}
            
            <!-- PWR Vessel -->
            <rect x="50" y="50" width="200" height="300" rx="40" ry="40" fill="url(#coolantGrad)" stroke="#bdc3c7" stroke-width="5" />
            
            <!-- Pressurizer (Side Tank) -->
            <rect x="260" y="80" width="30" height="80" rx="5" fill="#7f8c8d" stroke="#bdc3c7" />
            <line x1="250" y1="120" x2="260" y2="120" stroke="#7f8c8d" stroke-width="5" />
            
            <!-- Pipes -->
            <path d="M 50 100 L 20 100 L 20 300 L 50 300" stroke="#3498db" stroke-width="8" fill="none" />
            
            <!-- Fuel -->
            <rect x="80" y="120" width="140" height="180" rx="5" fill="{core_color}" opacity="0.4" filter="url(#glow)">
                 <animate attributeName="opacity" values="0.4;0.6;0.4" dur="2s" repeatCount="indefinite" />
            </rect>
            
            <!-- Flux Glow -->
            <rect x="80" y="120" width="140" height="180" rx="5" fill="url(#cerenkovInfo)" opacity="{glow_opacity}" />

            <!-- Control Rods -->
            <g transform="translate(100, 30)">
                <rect x="0" y="0" width="100" height="20" fill="#95a5a6" />
                <rect x="20" y="20" width="10" height="{rod_height}" fill="#7f8c8d" />
                <rect x="50" y="20" width="10" height="{rod_height}" fill="#7f8c8d" />
                <rect x="80" y="20" width="10" height="{rod_height}" fill="#7f8c8d" />
            </g>
            
            <text x="150" y="380" font-family="monospace" fill="#7f8c8d" text-anchor="middle">PWR UNIT</text>
        </svg>
        """

    @staticmethod
    def get_bwr_svg(telemetry):
        # BWR: Steam separation zone at top, Boiling visualization
        temp = telemetry.get("temp", 300)
        flux = telemetry.get("flux", 0.0)
        rods_pos = telemetry.get("rods_pos", 50.0)
        void_fraction = telemetry.get("void_fraction", 0.0) # Bubbles
        
        core_color = VisualGenerator.get_color_from_temp(temp)
        glow_opacity = min(1.0, flux * 1.5)
        rod_height = 20 + (rods_pos / 100.0) * 160 
        
        bubbles_anim = ""
        if void_fraction > 0.01:
             bubbles_anim = f"""
             <circle cx="100" cy="200" r="5" fill="white" opacity="0.5"><animate attributeName="cy" from="200" to="50" dur="1s" repeatCount="indefinite"/></circle>
             <circle cx="150" cy="220" r="8" fill="white" opacity="0.5"><animate attributeName="cy" from="220" to="50" dur="0.8s" repeatCount="indefinite"/></circle>
             <circle cx="200" cy="210" r="4" fill="white" opacity="0.5"><animate attributeName="cy" from="210" to="50" dur="1.2s" repeatCount="indefinite"/></circle>
             """

        return f"""
        <svg width="300" height="400" viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
            {VisualGenerator.get_common_defs()}
            
            <!-- BWR Vessel (Taller, thinner top) -->
            <path d="M 50 100 L 50 350 Q 150 400 250 350 L 250 100 Q 150 0 50 100" fill="url(#coolantGrad)" stroke="#bdc3c7" stroke-width="5" />
            
            <!-- Steam Dome -->
            <path d="M 50 100 Q 150 0 250 100" fill="rgba(255,255,255,0.1)" />
            
            <!-- Fuel -->
            <rect x="80" y="150" width="140" height="150" fill="{core_color}" opacity="0.4" filter="url(#glow)" />
            <rect x="80" y="150" width="140" height="150" fill="url(#cerenkovInfo)" opacity="{glow_opacity}" />
            
            <!-- Bubbles -->
            <g clip-path="url(#bwrClip)">
                {bubbles_anim}
            </g>
            
            <!-- Control Rods (Comes from BOTTOM in BWR usually, but sticking to top for simplicity/consistency unless critical) -->
            <!-- Actually, let's do bottom for realism -->
            <g transform="translate(100, 300)">
                 <rect x="20" y="0" width="10" height="{rod_height}" fill="#333" transform="scale(1,-1)" />
                 <rect x="50" y="0" width="10" height="{rod_height}" fill="#333" transform="scale(1,-1)" />
                 <rect x="80" y="0" width="10" height="{rod_height}" fill="#333" transform="scale(1,-1)" />
            </g>

            <text x="150" y="380" font-family="monospace" fill="#7f8c8d" text-anchor="middle">BWR UNIT</text>
        </svg>
        """

    @staticmethod
    def get_rbmk_svg(telemetry):
        # RBMK: Distinct Channel Tubes, Upper Biological Shield
        temp = telemetry.get("temp", 300)
        flux = telemetry.get("flux", 0.0)
        rods_pos = telemetry.get("rods_pos", 50.0)
        
        core_color = VisualGenerator.get_color_from_temp(temp)
        glow_opacity = min(1.0, flux * 2.0)
        
        # Grid of channels
        channels = ""
        for i in range(5):
            x = 70 + (i * 35)
            # Channel Column
            channels += f'<rect x="{x}" y="100" width="20" height="200" fill="#2c3e50" stroke="#7f8c8d" />'
            # Fuel inside
            channels += f'<rect x="{x+5}" y="110" width="10" height="180" fill="{core_color}" opacity="{0.3 + glow_opacity*0.7}" />'
            # Control Rod (Visual simple)
            rh = (rods_pos/100.0) * 180
            channels += f'<rect x="{x+8}" y="80" width="4" height="{rh}" fill="#e74c3c" />'

        return f"""
        <svg width="300" height="400" viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
            {VisualGenerator.get_common_defs()}
            
            <!-- Concrete Shield -->
            <rect x="20" y="20" width="260" height="360" rx="5" fill="#34495e" stroke="#2c3e50" stroke-width="10" />
            
            <!-- Upper Bio Shield (Elena) -->
            <circle cx="150" cy="50" r="100" rx="120" ry="20" fill="#95a5a6" stroke="#7f8c8d" />
            
            <!-- Core Area -->
            <g>
                {channels}
            </g>
            
            <!-- Graphite Stack Glow -->
             <rect x="60" y="100" width="180" height="200" fill="url(#cerenkovInfo)" opacity="{glow_opacity}" style="mix-blend-mode: screen;" />

            <text x="150" y="380" font-family="monospace" fill="#e74c3c" text-anchor="middle">RBMK-1000</text>
        </svg>
        """
