"""
circuit_diagrams.py
Generates clean vector SVG schematic diagrams for all 15 electronic circuits in CircuitAI CAD style.
Includes distinct element IDs and data attributes for interactive component highlighting and tooltips.
"""

def generate_circuit_svg(slug):
    """Returns SVG string for the given circuit slug with interactive component IDs."""

    svg_header = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 240" class="w-100 rounded-3" id="circuitSvg" style="background: #0b1120; border: 1px solid rgba(255, 255, 255, 0.1);">
    <defs>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <filter id="activeGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <linearGradient id="wireGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#3b82f6" />
            <stop offset="100%" stop-color="#06b6d4" />
        </linearGradient>
    </defs>
    <!-- Background Grid -->
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
    </pattern>
    <rect width="500" height="240" fill="url(#grid)" />
    '''
    
    svg_footer = '</svg>'
    
    if slug in ['rc-low-pass', 'rc-high-pass']:
        body = '''
        <!-- Input Terminal Vin -->
        <circle cx="50" cy="120" r="4" fill="#3b82f6" filter="url(#glow)"/>
        <text x="35" y="115" fill="#94a3b8" font-size="12" font-weight="bold">Vin</text>
        <path d="M 50 120 L 120 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- Interactive Resistor R -->
        <g id="comp-R" class="svg-component-group" data-comp-name="Resistor R" style="cursor: pointer;">
            <rect x="120" y="105" width="60" height="30" fill="#1e293b" stroke="#3b82f6" stroke-width="2" rx="4" class="comp-shape"/>
            <text x="145" y="125" fill="#f8fafc" font-size="13" font-weight="bold" class="comp-label">R</text>
            <title>Resistor R</title>
        </g>
        <path d="M 180 120 L 320 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- Interactive Capacitor C to GND -->
        <path d="M 250 120 L 250 145" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <g id="comp-C" class="svg-component-group" data-comp-name="Capacitor C" style="cursor: pointer;">
            <line x1="230" y1="145" x2="270" y2="145" stroke="#06b6d4" stroke-width="3.5" class="comp-shape"/>
            <line x1="230" y1="155" x2="270" y2="155" stroke="#06b6d4" stroke-width="3.5" class="comp-shape"/>
            <text x="280" y="154" fill="#f8fafc" font-size="13" font-weight="bold" class="comp-label">C</text>
            <title>Capacitor C</title>
        </g>
        <path d="M 250 155 L 250 190" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- Ground GND -->
        <line x1="235" y1="190" x2="265" y2="190" stroke="#94a3b8" stroke-width="2"/>
        <line x1="242" y1="195" x2="258" y2="195" stroke="#94a3b8" stroke-width="2"/>
        <line x1="247" y1="200" x2="253" y2="200" stroke="#94a3b8" stroke-width="2"/>
        
        <!-- Output Terminal Vout -->
        <path d="M 320 120 L 440 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="440" cy="120" r="4" fill="#06b6d4" filter="url(#glow)"/>
        <text x="448" y="115" fill="#06b6d4" font-size="12" font-weight="bold">Vout</text>
        '''
        
    elif slug == 'rlc-resonant':
        body = '''
        <!-- RLC Resonant Circuit Schematic -->
        <circle cx="40" cy="120" r="4" fill="#3b82f6"/>
        <text x="25" y="115" fill="#94a3b8" font-size="12">Vin</text>
        <path d="M 40 120 L 100 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- R -->
        <g id="comp-R" class="svg-component-group" data-comp-name="Resistor R" style="cursor: pointer;">
            <rect x="100" y="105" width="50" height="30" fill="#1e293b" stroke="#3b82f6" stroke-width="2" rx="4"/>
            <text x="120" y="125" fill="#fff" font-size="12" font-weight="bold">R</text>
            <title>Resistor R</title>
        </g>
        <path d="M 150 120 L 210 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- Inductor L -->
        <g id="comp-L" class="svg-component-group" data-comp-name="Inductor L" style="cursor: pointer;">
            <path d="M 210 120 Q 220 100 230 120 Q 240 100 250 120 Q 260 100 270 120" fill="none" stroke="#22c55e" stroke-width="3"/>
            <text x="235" y="95" fill="#22c55e" font-size="12" font-weight="bold">L</text>
            <title>Inductor L</title>
        </g>
        <path d="M 270 120 L 330 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- Capacitor C to GND -->
        <path d="M 330 120 L 330 145" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <g id="comp-C" class="svg-component-group" data-comp-name="Capacitor C" style="cursor: pointer;">
            <line x1="310" y1="145" x2="350" y2="145" stroke="#06b6d4" stroke-width="3.5"/>
            <line x1="310" y1="155" x2="350" y2="155" stroke="#06b6d4" stroke-width="3.5"/>
            <text x="360" y="154" fill="#fff" font-size="12" font-weight="bold">C</text>
            <title>Capacitor C</title>
        </g>
        <path d="M 330 155 L 330 190" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        
        <!-- Ground -->
        <line x1="315" y1="190" x2="345" y2="190" stroke="#94a3b8" stroke-width="2"/>
        <line x1="322" y1="195" x2="338" y2="195" stroke="#94a3b8" stroke-width="2"/>
        
        <!-- Vout -->
        <path d="M 330 120 L 440 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="440" cy="120" r="4" fill="#06b6d4"/>
        <text x="448" y="115" fill="#06b6d4" font-size="12" font-weight="bold">Vout</text>
        '''

    elif slug == 'active-filter':
        body = '''
        <!-- Active Sallen Key Filter Diagram -->
        <circle cx="40" cy="120" r="4" fill="#3b82f6"/>
        <text x="25" y="115" fill="#94a3b8" font-size="11">Vin</text>
        <path d="M 40 120 L 100 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        
        <g id="comp-R1" class="svg-component-group" data-comp-name="Resistor R1">
            <rect x="100" y="110" width="40" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
            <text x="112" y="125" fill="#fff" font-size="11">R1</text>
            <title>Resistor R1</title>
        </g>
        <path d="M 140 120 L 200 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        
        <g id="comp-R2" class="svg-component-group" data-comp-name="Resistor R2">
            <rect x="200" y="110" width="40" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
            <text x="212" y="125" fill="#fff" font-size="11">R2</text>
            <title>Resistor R2</title>
        </g>
        <path d="M 240 120 L 300 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        
        <!-- Op-Amp Triangle -->
        <polygon points="300,80 300,160 380,120" fill="#1e293b" stroke="#7c3aed" stroke-width="2.5" filter="url(#glow)"/>
        <text x="310" y="110" fill="#22c55e" font-size="14">+</text>
        <text x="310" y="140" fill="#ef4444" font-size="14">-</text>
        
        <g id="comp-C1" class="svg-component-group" data-comp-name="Capacitor C1">
            <line x1="170" y1="120" x2="170" y2="60" stroke="url(#wireGrad)" stroke-width="2"/>
            <line x1="170" y1="60" x2="340" y2="60" stroke="url(#wireGrad)" stroke-width="2"/>
            <line x1="340" y1="60" x2="340" y2="120" stroke="url(#wireGrad)" stroke-width="2"/>
            <text x="245" y="55" fill="#06b6d4" font-size="11">C1</text>
            <title>Capacitor C1</title>
        </g>

        <path d="M 380 120 L 450 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        <circle cx="450" cy="120" r="4" fill="#06b6d4"/>
        <text x="430" y="105" fill="#06b6d4" font-size="11">Vout</text>
        '''
        
    elif slug in ['common-emitter', 'common-collector', 'common-base']:
        body = '''
        <!-- BJT Transistor Schematic -->
        <circle cx="250" cy="120" r="40" fill="#1e293b" stroke="#3b82f6" stroke-width="2" filter="url(#glow)"/>
        <line x1="230" y1="100" x2="230" y2="140" stroke="#f8fafc" stroke-width="3"/>
        <line x1="170" y1="120" x2="230" y2="120" stroke="url(#wireGrad)" stroke-width="2"/>
        
        <!-- Collector & RC -->
        <line x1="230" y1="110" x2="270" y2="80" stroke="url(#wireGrad)" stroke-width="2"/>
        <line x1="270" y1="80" x2="270" y2="40" stroke="url(#wireGrad)" stroke-width="2"/>
        <g id="comp-RC" class="svg-component-group" data-comp-name="Collector Load RC">
            <rect x="250" y="45" width="40" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
            <text x="260" y="60" fill="#fff" font-size="11">RC</text>
            <title>Collector Load RC</title>
        </g>
        
        <!-- Emitter & RE -->
        <line x1="230" y1="130" x2="270" y2="160" stroke="url(#wireGrad)" stroke-width="2"/>
        <polygon points="265,155 270,160 260,163" fill="#06b6d4"/>
        <line x1="270" y1="160" x2="270" y2="200" stroke="url(#wireGrad)" stroke-width="2"/>
        <g id="comp-RE" class="svg-component-group" data-comp-name="Emitter Resistor RE">
            <rect x="250" y="170" width="40" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
            <text x="260" y="185" fill="#fff" font-size="11">RE</text>
            <title>Emitter Resistor RE</title>
        </g>
        
        <text x="140" y="115" fill="#94a3b8" font-size="11">Vin</text>
        <text x="280" y="35" fill="#22c55e" font-size="11">+VCC</text>
        '''
        
    elif slug in ['inverting-opamp', 'non-inverting-opamp', 'differential-amplifier', 'instrumentation-amplifier']:
        body = '''
        <!-- Op Amp Schematic -->
        <polygon points="200,60 200,180 320,120" fill="#1e293b" stroke="#7c3aed" stroke-width="3" filter="url(#glow)"/>
        <text x="210" y="95" fill="#ef4444" font-size="18" font-weight="bold">-</text>
        <text x="210" y="155" fill="#22c55e" font-size="18" font-weight="bold">+</text>
        
        <!-- Input Rin / R1 -->
        <path d="M 80 90 L 140 90" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        <g id="comp-Rin" class="svg-component-group" data-comp-name="Input Resistor Rin">
            <rect x="110" y="80" width="40" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
            <text x="120" y="95" fill="#fff" font-size="10">Rin</text>
            <title>Input Resistor Rin</title>
        </g>
        <g id="comp-R1" class="svg-component-group" data-comp-name="Ground Resistor R1">
            <!-- Alternative alias for non-inverting -->
            <title>Resistor R1</title>
        </g>
        <path d="M 150 90 L 200 90" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        
        <!-- Feedback Rf / R2 -->
        <path d="M 180 90 L 180 30 L 340 30 L 340 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        <g id="comp-Rf" class="svg-component-group" data-comp-name="Feedback Resistor Rf">
            <rect x="230" y="20" width="50" height="20" fill="#1e293b" stroke="#7c3aed" stroke-width="2"/>
            <text x="245" y="35" fill="#fff" font-size="11">Rf</text>
            <title>Feedback Resistor Rf</title>
        </g>
        <g id="comp-R2" class="svg-component-group" data-comp-name="Feedback Resistor R2">
            <title>Resistor R2</title>
        </g>
        
        <!-- Output -->
        <path d="M 320 120 L 430 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="430" cy="120" r="5" fill="#06b6d4" filter="url(#glow)"/>
        <text x="440" y="125" fill="#06b6d4" font-size="12" font-weight="bold">Vout</text>
        '''
        
    elif slug == 'rc-oscillator':
        body = '''
        <!-- RC Oscillator Diagram -->
        <rect x="60" y="90" width="60" height="60" fill="#1e293b" stroke="#7c3aed" stroke-width="2" rx="6"/>
        <text x="75" y="125" fill="#7c3aed" font-size="12" font-weight="bold">Amp</text>
        
        <path d="M 120 120 L 180 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        <g id="comp-R" class="svg-component-group" data-comp-name="Phase Shift Resistor R">
            <rect x="180" y="110" width="30" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
            <text x="190" y="124" fill="#fff" font-size="10">R</text>
            <title>Resistor R</title>
        </g>
        
        <path d="M 210 120 L 270 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        <g id="comp-C" class="svg-component-group" data-comp-name="Phase Shift Capacitance C">
            <rect x="270" y="110" width="30" height="20" fill="#1e293b" stroke="#06b6d4" stroke-width="1.5"/>
            <text x="280" y="124" fill="#fff" font-size="10">C</text>
            <title>Capacitor C</title>
        </g>
        
        <path d="M 300 120 L 440 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="440" cy="120" r="5" fill="#22c55e" filter="url(#glow)"/>
        <text x="410" y="105" fill="#22c55e" font-size="12" font-weight="bold">Vout (Sine)</text>
        '''
        
    elif slug == 'rectifier':
        body = '''
        <polygon points="200,60 260,120 200,180 140,120" fill="#1e293b" stroke="#06b6d4" stroke-width="2" filter="url(#glow)"/>
        <text x="185" y="125" fill="#3b82f6" font-size="13" font-weight="bold">Bridge</text>
        
        <path d="M 40 120 L 140 120" stroke="url(#wireGrad)" stroke-width="2" fill="none"/>
        <text x="50" y="105" fill="#94a3b8" font-size="12">Vin (AC)</text>
        
        <g id="comp-RL" class="svg-component-group" data-comp-name="Load Resistor RL">
            <rect x="300" y="110" width="50" height="20" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
            <text x="315" y="125" fill="#fff" font-size="11">RL</text>
            <title>Load Resistor RL</title>
        </g>
        
        <path d="M 260 120 L 420 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="420" cy="120" r="5" fill="#22c55e" filter="url(#glow)"/>
        <text x="430" y="125" fill="#22c55e" font-size="12" font-weight="bold">Vdc</text>
        '''
        
    else: # Buck & Boost Converters
        body = '''
        <rect x="180" y="70" width="140" height="100" fill="#1e293b" stroke="#2563eb" stroke-width="2.5" rx="8" filter="url(#glow)"/>
        <text x="210" y="115" fill="#3b82f6" font-size="14" font-weight="bold">Switching</text>
        
        <g id="comp-L" class="svg-component-group" data-comp-name="Inductor L">
            <text x="200" y="135" fill="#22c55e" font-size="12" font-weight="bold">Inductor L</text>
            <title>Inductor L</title>
        </g>
        <g id="comp-C" class="svg-component-group" data-comp-name="Capacitor C">
            <text x="200" y="150" fill="#06b6d4" font-size="11">Capacitor C</text>
            <title>Capacitor C</title>
        </g>

        <path d="M 50 120 L 180 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="50" cy="120" r="5" fill="#3b82f6"/>
        <text x="40" y="100" fill="#3b82f6" font-size="12" font-weight="bold">Vin</text>
        
        <path d="M 320 120 L 440 120" stroke="url(#wireGrad)" stroke-width="2.5" fill="none"/>
        <circle cx="440" cy="120" r="5" fill="#22c55e"/>
        <text x="420" y="100" fill="#22c55e" font-size="12" font-weight="bold">Vout</text>
        '''

    return svg_header + body + svg_footer
