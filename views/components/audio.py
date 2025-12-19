
import streamlit.components.v1 as components

def render_audio_engine(telemetry, sound_enabled=True):
    """
    Injects Invisible JavaScript to play sounds based on state.
    Uses Web Audio API for procdural sound generation (no assets needed).
    """
    if not sound_enabled:
        return

    # Extract Triggers
    scram = telemetry.get("scram", False)
    high_rads = telemetry.get("radiation_released", 0) > 0.05
    rad_level = telemetry.get("radiation_released", 0)
    melted = telemetry.get("melted", False)
    alarms_active = len(telemetry.get("alerts", [])) > 0
    
    # JS Logic
    js_code = f"""
    <script>
        // Singleton Audio Context
        if (!window.audioCtx) {{
            window.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }}
        
        const ctx = window.audioCtx;
        
        // --- SYNTHESIZERS ---
        
        function playKlaxon() {{
            // Dual sawtooth wave for harsh alarm
            const osc1 = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc1.type = 'sawtooth';
            osc1.frequency.setValueAtTime(400, ctx.currentTime);
            osc1.frequency.linearRampToValueAtTime(200, ctx.currentTime + 0.5);
            
            osc2.type = 'square';
            osc2.frequency.setValueAtTime(405, ctx.currentTime); // dissonant
            osc2.frequency.linearRampToValueAtTime(205, ctx.currentTime + 0.5);
            
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
            
            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(ctx.destination);
            
            osc1.start();
            osc2.start();
            osc1.stop(ctx.currentTime + 0.5);
            osc2.stop(ctx.currentTime + 0.5);
        }}
        
        function playGeiger() {{
            // White noise click
            const bufferSize = ctx.sampleRate * 0.005; // 5ms
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            
            for (let i = 0; i < bufferSize; i++) {{
                data[i] = Math.random() * 2 - 1;
            }}
            
            const noise = ctx.createBufferSource();
            noise.buffer = buffer;
            const gain = ctx.createGain();
            gain.gain.value = 0.5;
            
            noise.connect(gain);
            gain.connect(ctx.destination);
            noise.start();
        }}
        
        function playRumble() {{
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(50, ctx.currentTime);
            
            // LFO for modulation
            const lfo = ctx.createOscillator();
            lfo.frequency.value = 10;
            const lfoGain = ctx.createGain();
            lfoGain.gain.value = 500;
            lfo.connect(lfoGain);
            lfoGain.connect(osc.frequency);
            
            gain.gain.setValueAtTime(0.05, ctx.currentTime);
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            lfo.start();
            osc.stop(ctx.currentTime + 0.2);
            lfo.stop(ctx.currentTime + 0.2);
        }}

        function playBeep() {{
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(800, ctx.currentTime);
            gain.gain.setValueAtTime(0.05, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.1);
        }}

        // --- TRIGGER LOGIC ---
        
        // Resume context if suspended (browser policy)
        if (ctx.state === 'suspended') {{
            ctx.resume();
        }}

        const now = Date.now();
        
        // 1. SCRAM KLAXON (Every 1s)
        if ({str(scram).lower()} || {str(alarms_active).lower()}) {{
             if (!window.lastKlaxon || now - window.lastKlaxon > 800) {{
                 playKlaxon();
                 window.lastKlaxon = now;
             }}
        }}
        
        // 2. GEIGER (Random based on rad level)
        let radLevel = {rad_level};
        if (radLevel > 0) {{
            // higher rads = lower interval = more clicks
            // e.g. 1.0 Sv = 10% chance per frame? 
            // Let's just burst click
            let clicks = Math.min(20, Math.floor(radLevel * 5));
            if (Math.random() < 0.5) {{
                 for(let i=0; i<clicks; i++) {{
                     setTimeout(playGeiger, Math.random() * 100);
                 }}
            }}
        }}

        // 3. MELTDOWN RUMBLE
        if ({str(melted).lower()}) {{
            if (Math.random() < 0.3) playRumble();
        }}
        
    </script>
    """
    
    components.html(js_code, height=0, width=0)
