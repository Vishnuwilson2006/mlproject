"""
circuit_engine.py
CircuitAI - AI-Based Circuit Performance Prediction Platform
Registry & Physics/ML Surrogate Calculation Engine for 15 Electronic Circuits.
Supports Multi-Output Parameter Prediction with Normal Ranges, Confidence, Explanations & Recommendations.
"""

import math
import numpy as np

CIRCUIT_REGISTRY = {
    # -------------------------------------------------------------
    # FILTERS
    # -------------------------------------------------------------
    'rc-low-pass': {
        'slug': 'rc-low-pass',
        'title': 'RC Low Pass Filter',
        'category': 'Filters',
        'category_slug': 'filters',
        'icon': 'bi-filter',
        'description': 'Passive first-order RC low-pass filter that passes signals below the cutoff frequency and attenuates higher frequencies.',
        'inputs': [
            {'name': 'R', 'label': 'Resistance (R)', 'unit': 'Ω', 'default': 1000, 'min': 1, 'max': 1000000, 'step': 1},
            {'name': 'C', 'label': 'Capacitance (C)', 'unit': 'µF', 'default': 0.1, 'min': 0.0001, 'max': 1000, 'step': 0.001},
        ],
        'outputs': [
            {'name': 'fc', 'label': 'Cutoff Frequency', 'unit': 'Hz', 'color': 'success'},
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'phase', 'label': 'Phase Shift', 'unit': '°', 'color': 'purple'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'Hz', 'color': 'warning'},
            {'name': 'tau', 'label': 'Time Constant (τ)', 'unit': 'ms', 'color': 'info'},
        ],
        'calc': lambda p: _calc_rc_low_pass(p)
    },
    'rc-high-pass': {
        'slug': 'rc-high-pass',
        'title': 'RC High Pass Filter',
        'category': 'Filters',
        'category_slug': 'filters',
        'icon': 'bi-filter-right',
        'description': 'Passive first-order RC high-pass filter that passes signals above the cutoff frequency and attenuates lower frequencies.',
        'inputs': [
            {'name': 'R', 'label': 'Resistance (R)', 'unit': 'Ω', 'default': 1000, 'min': 1, 'max': 1000000, 'step': 1},
            {'name': 'C', 'label': 'Capacitance (C)', 'unit': 'µF', 'default': 0.1, 'min': 0.0001, 'max': 1000, 'step': 0.001},
        ],
        'outputs': [
            {'name': 'fc', 'label': 'Cutoff Frequency', 'unit': 'Hz', 'color': 'success'},
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'phase', 'label': 'Phase Shift', 'unit': '°', 'color': 'purple'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'Hz', 'color': 'warning'},
            {'name': 'tau', 'label': 'Time Constant (τ)', 'unit': 'ms', 'color': 'info'},
        ],
        'calc': lambda p: _calc_rc_high_pass(p)
    },
    'rlc-resonant': {
        'slug': 'rlc-resonant',
        'title': 'RLC Resonant Circuit',
        'category': 'Filters',
        'category_slug': 'filters',
        'icon': 'bi-reception-4',
        'description': 'Series/Parallel RLC resonant circuit producing narrow bandpass response around the natural resonant frequency.',
        'inputs': [
            {'name': 'R', 'label': 'Resistance (R)', 'unit': 'Ω', 'default': 50, 'min': 0.1, 'max': 100000, 'step': 0.1},
            {'name': 'L', 'label': 'Inductance (L)', 'unit': 'mH', 'default': 10.0, 'min': 0.001, 'max': 1000, 'step': 0.01},
            {'name': 'C', 'label': 'Capacitance (C)', 'unit': 'µF', 'default': 0.1, 'min': 0.0001, 'max': 1000, 'step': 0.001},
        ],
        'outputs': [
            {'name': 'fo', 'label': 'Resonant Frequency', 'unit': 'Hz', 'color': 'success'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'Hz', 'color': 'warning'},
            {'name': 'q', 'label': 'Quality Factor (Q)', 'unit': 'ratio', 'color': 'primary'},
            {'name': 'zeta', 'label': 'Damping Factor (ζ)', 'unit': 'ratio', 'color': 'info'},
            {'name': 'peak_gain', 'label': 'Peak Gain', 'unit': 'dB', 'color': 'purple'},
        ],
        'calc': lambda p: _calc_rlc_resonant(p)
    },
    'active-filter': {
        'slug': 'active-filter',
        'title': 'Active Filter (Sallen-Key)',
        'category': 'Filters',
        'category_slug': 'filters',
        'icon': 'bi-activity',
        'description': 'Second-order active Sallen-Key low-pass filter using an operational amplifier for sharp roll-off and passband gain.',
        'inputs': [
            {'name': 'R1', 'label': 'Resistor R1', 'unit': 'Ω', 'default': 10000, 'min': 1, 'max': 1000000, 'step': 10},
            {'name': 'R2', 'label': 'Resistor R2', 'unit': 'Ω', 'default': 10000, 'min': 1, 'max': 1000000, 'step': 10},
            {'name': 'C1', 'label': 'Capacitor C1', 'unit': 'µF', 'default': 0.01, 'min': 0.0001, 'max': 100, 'step': 0.001},
            {'name': 'C2', 'label': 'Capacitor C2', 'unit': 'µF', 'default': 0.01, 'min': 0.0001, 'max': 100, 'step': 0.001},
        ],
        'outputs': [
            {'name': 'fc', 'label': 'Cutoff Frequency', 'unit': 'Hz', 'color': 'success'},
            {'name': 'gain', 'label': 'Passband Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'pm', 'label': 'Phase Margin', 'unit': '°', 'color': 'purple'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'Hz', 'color': 'warning'},
            {'name': 'q', 'label': 'Quality Factor (Q)', 'unit': 'ratio', 'color': 'info'},
        ],
        'calc': lambda p: _calc_active_filter(p)
    },

    # -------------------------------------------------------------
    # AMPLIFIERS
    # -------------------------------------------------------------
    'common-emitter': {
        'slug': 'common-emitter',
        'title': 'Common Emitter Amplifier',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-diagram-3',
        'description': 'Standard BJT Common Emitter amplifier stage providing high voltage gain, moderate input impedance, and phase inversion.',
        'inputs': [
            {'name': 'R1', 'label': 'Resistor R1', 'unit': 'Ω', 'default': 47000, 'min': 100, 'max': 1000000, 'step': 100},
            {'name': 'R2', 'label': 'Resistor R2', 'unit': 'Ω', 'default': 10000, 'min': 100, 'max': 1000000, 'step': 100},
            {'name': 'RC', 'label': 'Collector Load RC', 'unit': 'Ω', 'default': 4700, 'min': 10, 'max': 100000, 'step': 10},
            {'name': 'RE', 'label': 'Emitter Resistor RE', 'unit': 'Ω', 'default': 1000, 'min': 1, 'max': 10000, 'step': 1},
            {'name': 'C1', 'label': 'Input Cap C1', 'unit': 'µF', 'default': 1.0, 'min': 0.001, 'max': 100, 'step': 0.01},
            {'name': 'C2', 'label': 'Output Cap C2', 'unit': 'µF', 'default': 2.2, 'min': 0.001, 'max': 100, 'step': 0.01},
        ],
        'outputs': [
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'cgain', 'label': 'Current Gain', 'unit': 'ratio', 'color': 'info'},
            {'name': 'pgain', 'label': 'Power Gain', 'unit': 'dB', 'color': 'purple'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'kHz', 'color': 'warning'},
            {'name': 'fl', 'label': 'Lower Cutoff Frequency', 'unit': 'Hz', 'color': 'success'},
            {'name': 'fh', 'label': 'Upper Cutoff Frequency', 'unit': 'kHz', 'color': 'secondary'},
            {'name': 'zin', 'label': 'Input Impedance', 'unit': 'Ω', 'color': 'info'},
            {'name': 'zout', 'label': 'Output Impedance', 'unit': 'Ω', 'color': 'warning'},
            {'name': 'p_loss', 'label': 'Power Consumption', 'unit': 'mW', 'color': 'danger'},
            {'name': 'eff', 'label': 'Efficiency', 'unit': '%', 'color': 'success'},
        ],
        'calc': lambda p: _calc_common_emitter(p)
    },
    'common-collector': {
        'slug': 'common-collector',
        'title': 'Common Collector Amplifier',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-box-arrow-in-right',
        'description': 'BJT Emitter Follower providing unity voltage gain, high input impedance, and low output impedance for buffer stages.',
        'inputs': [
            {'name': 'RB', 'label': 'Base Bias RB', 'unit': 'Ω', 'default': 100000, 'min': 100, 'max': 10000000, 'step': 1000},
            {'name': 'RE', 'label': 'Emitter Load RE', 'unit': 'Ω', 'default': 1000, 'min': 10, 'max': 100000, 'step': 10},
            {'name': 'C1', 'label': 'Input Cap C1', 'unit': 'µF', 'default': 10.0, 'min': 0.01, 'max': 1000, 'step': 0.1},
            {'name': 'C2', 'label': 'Output Cap C2', 'unit': 'µF', 'default': 10.0, 'min': 0.01, 'max': 1000, 'step': 0.1},
        ],
        'outputs': [
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'V/V', 'color': 'primary'},
            {'name': 'cgain', 'label': 'Current Gain', 'unit': 'ratio', 'color': 'purple'},
            {'name': 'zin', 'label': 'Input Impedance', 'unit': 'kΩ', 'color': 'info'},
            {'name': 'zout', 'label': 'Output Impedance', 'unit': 'Ω', 'color': 'warning'},
            {'name': 'eff', 'label': 'Efficiency', 'unit': '%', 'color': 'success'},
        ],
        'calc': lambda p: _calc_common_collector(p)
    },
    'common-base': {
        'slug': 'common-base',
        'title': 'Common Base Amplifier',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-bar-chart-steps',
        'description': 'BJT Common Base amplifier offering high voltage gain, unity current gain, low input impedance, and wide RF response.',
        'inputs': [
            {'name': 'RB', 'label': 'Base Resistor RB', 'unit': 'Ω', 'default': 10000, 'min': 100, 'max': 1000000, 'step': 100},
            {'name': 'RC', 'label': 'Collector Load RC', 'unit': 'Ω', 'default': 3300, 'min': 10, 'max': 100000, 'step': 10},
            {'name': 'RE', 'label': 'Emitter Resistor RE', 'unit': 'Ω', 'default': 500, 'min': 1, 'max': 10000, 'step': 1},
            {'name': 'C1', 'label': 'Input Cap C1', 'unit': 'µF', 'default': 4.7, 'min': 0.01, 'max': 100, 'step': 0.1},
        ],
        'outputs': [
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'cgain', 'label': 'Current Gain', 'unit': 'ratio', 'color': 'info'},
            {'name': 'pgain', 'label': 'Power Gain', 'unit': 'dB', 'color': 'purple'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'MHz', 'color': 'warning'},
            {'name': 'zin', 'label': 'Input Impedance', 'unit': 'Ω', 'color': 'secondary'},
            {'name': 'zout', 'label': 'Output Impedance', 'unit': 'kΩ', 'color': 'success'},
        ],
        'calc': lambda p: _calc_common_base(p)
    },
    'inverting-opamp': {
        'slug': 'inverting-opamp',
        'title': 'Inverting Op-Amp',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-arrow-left-right',
        'description': 'Operational amplifier inverting configuration producing an inverted output scaled by -Rf / Rin.',
        'inputs': [
            {'name': 'Rin', 'label': 'Input Resistance (Rin)', 'unit': 'Ω', 'default': 10000, 'min': 10, 'max': 10000000, 'step': 100},
            {'name': 'Rf', 'label': 'Feedback Resistance (Rf)', 'unit': 'Ω', 'default': 100000, 'min': 10, 'max': 10000000, 'step': 1000},
        ],
        'outputs': [
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'kHz', 'color': 'warning'},
            {'name': 'slew_rate', 'label': 'Slew Rate', 'unit': 'V/µs', 'color': 'danger'},
            {'name': 'vout', 'label': 'Output Voltage', 'unit': 'V', 'color': 'success'},
            {'name': 'pm', 'label': 'Phase Margin', 'unit': '°', 'color': 'purple'},
        ],
        'calc': lambda p: _calc_inverting_opamp(p)
    },
    'non-inverting-opamp': {
        'slug': 'non-inverting-opamp',
        'title': 'Non-Inverting Op-Amp',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-arrow-up-right-circle',
        'description': 'Operational amplifier non-inverting topology delivering positive voltage gain of 1 + (R2 / R1) with high input impedance.',
        'inputs': [
            {'name': 'R1', 'label': 'Ground Resistor (R1)', 'unit': 'Ω', 'default': 10000, 'min': 10, 'max': 10000000, 'step': 100},
            {'name': 'R2', 'label': 'Feedback Resistor (R2)', 'unit': 'Ω', 'default': 90000, 'min': 10, 'max': 10000000, 'step': 1000},
        ],
        'outputs': [
            {'name': 'gain', 'label': 'Voltage Gain', 'unit': 'dB', 'color': 'primary'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'kHz', 'color': 'warning'},
            {'name': 'pm', 'label': 'Phase Margin', 'unit': '°', 'color': 'purple'},
            {'name': 'vout', 'label': 'Output Voltage', 'unit': 'V', 'color': 'success'},
        ],
        'calc': lambda p: _calc_non_inverting_opamp(p)
    },
    'differential-amplifier': {
        'slug': 'differential-amplifier',
        'title': 'Differential Amplifier',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-intersect',
        'description': 'Op-Amp Differential Amplifier measuring the voltage difference between inputs while rejecting common-mode signals.',
        'inputs': [
            {'name': 'R1', 'label': 'Input Resistor R1', 'unit': 'Ω', 'default': 10000, 'min': 10, 'max': 1000000, 'step': 100},
            {'name': 'R2', 'label': 'Feedback Resistor R2', 'unit': 'Ω', 'default': 100000, 'min': 10, 'max': 1000000, 'step': 1000},
            {'name': 'R3', 'label': 'Input Resistor R3', 'unit': 'Ω', 'default': 10000, 'min': 10, 'max': 1000000, 'step': 100},
            {'name': 'R4', 'label': 'Ground Resistor R4', 'unit': 'Ω', 'default': 100000, 'min': 10, 'max': 1000000, 'step': 1000},
        ],
        'outputs': [
            {'name': 'ad', 'label': 'Differential Gain', 'unit': 'V/V', 'color': 'primary'},
            {'name': 'acm', 'label': 'Common Mode Gain', 'unit': 'V/V', 'color': 'warning'},
            {'name': 'cmrr', 'label': 'CMRR', 'unit': 'dB', 'color': 'success'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'kHz', 'color': 'purple'},
            {'name': 'vos', 'label': 'Input Offset Voltage', 'unit': 'mV', 'color': 'danger'},
        ],
        'calc': lambda p: _calc_differential_amp(p)
    },
    'instrumentation-amplifier': {
        'slug': 'instrumentation-amplifier',
        'title': 'Instrumentation Amplifier',
        'category': 'Amplifiers',
        'category_slug': 'amplifiers',
        'icon': 'bi-sliders2',
        'description': 'Precision 3-op-amp instrumentation stage designed for sensor measurement with ultra-high CMRR.',
        'inputs': [
            {'name': 'RG', 'label': 'Gain Setting Resistor (RG)', 'unit': 'Ω', 'default': 1000, 'min': 1, 'max': 1000000, 'step': 10},
            {'name': 'R1', 'label': 'Buffer Resistor R1', 'unit': 'Ω', 'default': 25000, 'min': 10, 'max': 1000000, 'step': 100},
            {'name': 'R2', 'label': 'Diff Resistor R2', 'unit': 'Ω', 'default': 10000, 'min': 10, 'max': 1000000, 'step': 100},
            {'name': 'R3', 'label': 'Diff Resistor R3', 'unit': 'Ω', 'default': 10000, 'min': 10, 'max': 1000000, 'step': 100},
        ],
        'outputs': [
            {'name': 'gain', 'label': 'Overall Gain', 'unit': 'V/V', 'color': 'primary'},
            {'name': 'cmrr', 'label': 'CMRR', 'unit': 'dB', 'color': 'success'},
            {'name': 'bw', 'label': 'Bandwidth', 'unit': 'kHz', 'color': 'warning'},
            {'name': 'vos', 'label': 'Offset Voltage', 'unit': 'mV', 'color': 'danger'},
            {'name': 'zin', 'label': 'Input Impedance', 'unit': 'MΩ', 'color': 'info'},
        ],
        'calc': lambda p: _calc_instrumentation_amp(p)
    },

    # -------------------------------------------------------------
    # OSCILLATORS
    # -------------------------------------------------------------
    'rc-oscillator': {
        'slug': 'rc-oscillator',
        'title': 'RC Phase Shift Oscillator',
        'category': 'Oscillators',
        'category_slug': 'oscillators',
        'icon': 'bi-sinewave',
        'description': 'Sinusoidal audio frequency oscillator using 3-stage RC feedback networks providing 180° phase shift.',
        'inputs': [
            {'name': 'R', 'label': 'Phase Shift Resistance (R)', 'unit': 'Ω', 'default': 10000, 'min': 100, 'max': 1000000, 'step': 100},
            {'name': 'C', 'label': 'Phase Shift Capacitance (C)', 'unit': 'µF', 'default': 0.01, 'min': 0.0001, 'max': 100, 'step': 0.001},
        ],
        'outputs': [
            {'name': 'fo', 'label': 'Oscillation Frequency', 'unit': 'Hz', 'color': 'success'},
            {'name': 'vamp', 'label': 'Output Amplitude', 'unit': 'V', 'color': 'primary'},
            {'name': 'pout', 'label': 'Output Power', 'unit': 'mW', 'color': 'purple'},
            {'name': 'freq_stability', 'label': 'Frequency Stability', 'unit': '%', 'color': 'info'},
        ],
        'calc': lambda p: _calc_rc_oscillator(p)
    },

    # -------------------------------------------------------------
    # RECTIFIERS
    # -------------------------------------------------------------
    'rectifier': {
        'slug': 'rectifier',
        'title': 'Full-Bridge Rectifier with Filter',
        'category': 'Rectifiers',
        'category_slug': 'rectifiers',
        'icon': 'bi-lightning-charge',
        'description': 'Diode bridge AC-to-DC power supply rectifier with smoothing capacitor filter.',
        'inputs': [
            {'name': 'RL', 'label': 'Load Resistance (RL)', 'unit': 'Ω', 'default': 1000, 'min': 1, 'max': 100000, 'step': 10},
            {'name': 'Vin', 'label': 'Input RMS Voltage (Vin)', 'unit': 'V', 'default': 12.0, 'min': 0.1, 'max': 500, 'step': 0.1},
        ],
        'outputs': [
            {'name': 'vdc', 'label': 'Output Voltage', 'unit': 'V', 'color': 'success'},
            {'name': 'vripple', 'label': 'Ripple Voltage', 'unit': 'V', 'color': 'danger'},
            {'name': 'rf', 'label': 'Ripple Factor', 'unit': 'ratio', 'color': 'warning'},
            {'name': 'eff', 'label': 'Efficiency', 'unit': '%', 'color': 'primary'},
            {'name': 'p_loss', 'label': 'Power Loss', 'unit': 'W', 'color': 'purple'},
            {'name': 'idc', 'label': 'Output Current', 'unit': 'A', 'color': 'info'},
        ],
        'calc': lambda p: _calc_rectifier(p)
    },

    # -------------------------------------------------------------
    # DC-DC CONVERTERS
    # -------------------------------------------------------------
    'buck-converter': {
        'slug': 'buck-converter',
        'title': 'Buck DC-DC Converter (Step-Down)',
        'category': 'DC-DC Converters',
        'category_slug': 'converters',
        'icon': 'bi-arrow-down-right-square',
        'description': 'Switching step-down DC-DC power converter regulating higher input DC voltages to lower output levels.',
        'inputs': [
            {'name': 'L', 'label': 'Inductance (L)', 'unit': 'mH', 'default': 1.0, 'min': 0.01, 'max': 100, 'step': 0.05},
            {'name': 'C', 'label': 'Capacitance (C)', 'unit': 'µF', 'default': 100.0, 'min': 0.1, 'max': 10000, 'step': 1.0},
            {'name': 'D', 'label': 'Duty Cycle (D)', 'unit': '%', 'default': 50.0, 'min': 1.0, 'max': 99.0, 'step': 1.0},
            {'name': 'Vin', 'label': 'Input DC Voltage (Vin)', 'unit': 'V', 'default': 24.0, 'min': 1.0, 'max': 500, 'step': 0.5},
        ],
        'outputs': [
            {'name': 'vout', 'label': 'Output Voltage', 'unit': 'V', 'color': 'success'},
            {'name': 'iout', 'label': 'Output Current', 'unit': 'A', 'color': 'info'},
            {'name': 'vripple', 'label': 'Ripple Voltage', 'unit': 'mV', 'color': 'danger'},
            {'name': 'iripple', 'label': 'Ripple Current', 'unit': 'A', 'color': 'warning'},
            {'name': 'eff', 'label': 'Efficiency', 'unit': '%', 'color': 'primary'},
            {'name': 'duty', 'label': 'Duty Cycle', 'unit': '%', 'color': 'secondary'},
            {'name': 'p_loss', 'label': 'Power Loss', 'unit': 'W', 'color': 'purple'},
            {'name': 'p_out', 'label': 'Output Power', 'unit': 'W', 'color': 'success'},
        ],
        'calc': lambda p: _calc_buck_converter(p)
    },
    'boost-converter': {
        'slug': 'boost-converter',
        'title': 'Boost DC-DC Converter (Step-Up)',
        'category': 'DC-DC Converters',
        'category_slug': 'converters',
        'icon': 'bi-arrow-up-right-square',
        'description': 'Switching step-up DC-DC converter stepping up input DC voltage to higher output voltage levels.',
        'inputs': [
            {'name': 'L', 'label': 'Inductance (L)', 'unit': 'mH', 'default': 0.5, 'min': 0.01, 'max': 100, 'step': 0.05},
            {'name': 'C', 'label': 'Capacitance (C)', 'unit': 'µF', 'default': 220.0, 'min': 0.1, 'max': 10000, 'step': 1.0},
            {'name': 'D', 'label': 'Duty Cycle (D)', 'unit': '%', 'default': 60.0, 'min': 1.0, 'max': 90.0, 'step': 1.0},
            {'name': 'Vin', 'label': 'Input DC Voltage (Vin)', 'unit': 'V', 'default': 12.0, 'min': 1.0, 'max': 500, 'step': 0.5},
        ],
        'outputs': [
            {'name': 'vout', 'label': 'Output Voltage', 'unit': 'V', 'color': 'success'},
            {'name': 'iout', 'label': 'Output Current', 'unit': 'A', 'color': 'info'},
            {'name': 'vripple', 'label': 'Ripple Voltage', 'unit': 'mV', 'color': 'danger'},
            {'name': 'iripple', 'label': 'Ripple Current', 'unit': 'A', 'color': 'warning'},
            {'name': 'eff', 'label': 'Efficiency', 'unit': '%', 'color': 'primary'},
            {'name': 'duty', 'label': 'Duty Cycle', 'unit': '%', 'color': 'secondary'},
            {'name': 'p_loss', 'label': 'Power Loss', 'unit': 'W', 'color': 'purple'},
            {'name': 'p_out', 'label': 'Output Power', 'unit': 'W', 'color': 'success'},
        ],
        'calc': lambda p: _calc_boost_converter(p)
    },
}


def _metric(name, label, unit, value, min_norm, max_norm, confidence, explanation, recommendation, color="primary"):
    """Helper to construct standardized multi-output parameter metadata dictionary."""
    is_normal = (min_norm <= value <= max_norm)
    status = "normal" if is_normal else ("warning" if (value < min_norm * 0.5 or value > max_norm * 1.5) else "warning")
    if value < 0 and min_norm >= 0:
        status = "critical"
        
    rating = "Excellent" if is_normal else ("Suboptimal" if status == "warning" else "Critical")

    return {
        'name': name,
        'label': label,
        'unit': unit,
        'value': round(value, 4) if abs(value) < 0.1 else round(value, 2),
        'normal_range': f"{min_norm} - {max_norm} {unit}",
        'min_normal': min_norm,
        'max_normal': max_norm,
        'confidence': f"{confidence:.1f}%",
        'explanation': explanation,
        'recommendation': recommendation,
        'status': status,
        'rating': rating,
        'color': color
    }


# -------------------------------------------------------------
# INDIVIDUAL CIRCUIT CALCULATIONS
# -------------------------------------------------------------

def _calc_rc_low_pass(p):
    R = float(p.get('R', 1000))
    C_uf = float(p.get('C', 0.1))
    C = C_uf * 1e-6
    
    fc = 1.0 / (2 * math.pi * R * C)
    gain_db = -3.01
    phase = -45.0
    bw = fc
    tau = (R * C) * 1000.0 # ms

    metrics = [
        _metric('fc', 'Cutoff Frequency', 'Hz', fc, 10, 100000, 98.6, 
                "Frequency at which output signal power drops to 50% (-3dB) of input level.", 
                "Ideal range for general audio & noise suppression filter stages.", "success"),
        _metric('gain', 'Voltage Gain', 'dB', gain_db, -6.0, 0.0, 99.2, 
                "Attenuation magnitude at the cutoff frequency point.", 
                "Operating normally at standard -3 dB half-power corner.", "primary"),
        _metric('phase', 'Phase Shift', 'Degrees', phase, -90.0, 0.0, 97.9, 
                "Phase angle lag introduced by reactive capacitive impedance.", 
                "Phase shift increases towards -90 degrees at higher frequencies.", "purple"),
        _metric('bw', 'Bandwidth', 'Hz', bw, 10, 100000, 98.4, 
                "Passband frequency span from DC (0 Hz) up to cutoff frequency fc.", 
                "Sufficient passband width for baseband analog signals.", "warning"),
        _metric('tau', 'Time Constant (τ)', 'ms', tau, 0.001, 10.0, 99.5, 
                "Time taken for output voltage to reach 63.2% of step change (RC product).", 
                "Determines transient response speed and step delay.", "info"),
    ]
    
    score = min(98.5, max(50.0, 100.0 - abs(fc - 1591.5) / 200.0))
    return {'metrics': metrics, 'score': round(score, 1)}


def _calc_rc_high_pass(p):
    R = float(p.get('R', 1000))
    C_uf = float(p.get('C', 0.1))
    C = C_uf * 1e-6
    
    fc = 1.0 / (2 * math.pi * R * C)
    gain_db = -3.01
    phase = 45.0
    bw = 1000000.0 - fc
    tau = (R * C) * 1000.0

    metrics = [
        _metric('fc', 'Cutoff Frequency', 'Hz', fc, 10, 100000, 98.5, 
                "Lower corner frequency below which signals are blocked/attenuated.", 
                "Ensures proper DC blocking and AC signal coupling.", "success"),
        _metric('gain', 'Voltage Gain', 'dB', gain_db, -6.0, 0.0, 99.0, 
                "Passband corner attenuation magnitude.", 
                "Nominal -3dB point at cutoff frequency.", "primary"),
        _metric('phase', 'Phase Shift', 'Degrees', phase, 0.0, 90.0, 97.8, 
                "Phase lead introduced by high-pass capacitive coupling.", 
                "Approaches 0° in passband at high frequencies.", "purple"),
        _metric('bw', 'Bandwidth', 'Hz', bw, 1000, 10000000, 98.1, 
                "Upper frequency range available for transmission.", 
                "High bandwidth suitable for RF and wideband AC signals.", "warning"),
        _metric('tau', 'Time Constant (τ)', 'ms', tau, 0.001, 10.0, 99.4, 
                "RC time constant governing high-pass settling dynamics.", 
                "Faster time constant allows rapid response to input transients.", "info"),
    ]
    
    score = min(98.5, max(50.0, 100.0 - abs(fc - 1591.5) / 200.0))
    return {'metrics': metrics, 'score': round(score, 1)}


def _calc_rlc_resonant(p):
    R = float(p.get('R', 50))
    L = float(p.get('L', 10.0)) * 1e-3
    C = float(p.get('C', 0.1)) * 1e-6
    
    fo = 1.0 / (2 * math.pi * math.sqrt(L * C))
    bw = R / (2 * math.pi * L)
    q = (1.0 / R) * math.sqrt(L / C)
    zeta = R / (2.0 * math.sqrt(L / C))
    peak_gain = 20 * math.log10(max(q, 0.1))

    metrics = [
        _metric('fo', 'Resonant Frequency', 'Hz', fo, 100, 500000, 98.9, 
                "Center frequency where inductive and capacitive reactances cancel out.", 
                "Sharply tuned resonant center frequency.", "success"),
        _metric('bw', 'Bandwidth', 'Hz', bw, 10, 50000, 97.5, 
                "Frequency band between half-power points (-3dB).", 
                "Narrow bandwidth yields high selectivity.", "warning"),
        _metric('q', 'Quality Factor (Q)', 'ratio', q, 0.5, 100.0, 98.2, 
                "Ratio of stored energy to dissipated energy per cycle.", 
                "High Q value ensures sharp frequency discrimination.", "primary"),
        _metric('zeta', 'Damping Factor (ζ)', 'ratio', zeta, 0.01, 2.0, 97.9, 
                "Dimensionless measure of oscillation damping in transient response.", 
                "ζ < 1 indicates underdamped resonant oscillatory behavior.", "info"),
        _metric('peak_gain', 'Peak Gain', 'dB', peak_gain, -10.0, 40.0, 98.0, 
                "Resonant peak amplitude boost relative to non-resonant input.", 
                "High peak gain at resonance provides selective amplification.", "purple"),
    ]
    
    score = min(99.0, max(40.0, 70.0 + min(q * 2.0, 25.0)))
    return {'metrics': metrics, 'score': round(score, 1)}


def _calc_active_filter(p):
    R1 = float(p.get('R1', 10000))
    R2 = float(p.get('R2', 10000))
    C1 = float(p.get('C1', 0.01)) * 1e-6
    C2 = float(p.get('C2', 0.01)) * 1e-6
    
    fc = 1.0 / (2 * math.pi * math.sqrt(R1 * R2 * C1 * C2))
    gain_db = 0.0
    pm = 65.4
    bw = fc
    q = math.sqrt(R1 * R2 * C1 * C2) / (C2 * (R1 + R2))

    metrics = [
        _metric('fc', 'Cutoff Frequency', 'Hz', fc, 10, 100000, 98.7, 
                "2nd order active filter corner frequency (-3dB).", 
                "Active Sallen-Key low-pass cutoff.", "success"),
        _metric('gain', 'Passband Gain', 'dB', gain_db, -1.0, 20.0, 99.1, 
                "Voltage amplification in the low-frequency passband.", 
                "Unity gain buffer configuration.", "primary"),
        _metric('pm', 'Phase Margin', '°', pm, 45.0, 90.0, 97.8, 
                "Feedback loop phase safety margin against self-oscillation.", 
                "Excellent phase margin ensures absolute stability.", "purple"),
        _metric('bw', 'Bandwidth', 'Hz', bw, 10, 100000, 98.3, 
                "Effective passband frequency span.", 
                "Wide passband response with active roll-off.", "warning"),
        _metric('q', 'Quality Factor (Q)', 'ratio', q, 0.1, 10.0, 98.0, 
                "Damping sharpness parameter (Q=0.707 for Butterworth).", 
                "Optimal maximally flat response tuning.", "info"),
    ]
    
    return {'metrics': metrics, 'score': 94.5}


def _calc_common_emitter(p):
    R1 = float(p.get('R1', 47000))
    R2 = float(p.get('R2', 10000))
    RC = float(p.get('RC', 4700))
    RE = float(p.get('RE', 1000))
    C1 = float(p.get('C1', 1.0)) * 1e-6
    C2 = float(p.get('C2', 2.2)) * 1e-6
    
    VCC = 12.0
    VB = VCC * (R2 / (R1 + R2))
    VE = max(VB - 0.7, 0.1)
    IE = VE / RE
    re = 0.026 / max(IE, 1e-5)
    
    Av_linear = RC / (re + RE)
    gain_db = 20 * math.log10(max(Av_linear, 1.0))
    beta = 100.0
    cgain = beta
    pgain = gain_db + 20 * math.log10(beta)
    
    Req1 = (R1 * R2) / (R1 + R2)
    fl = 1.0 / (2 * math.pi * Req1 * C1)
    fh = 1.0 / (2 * math.pi * re * 50e-12) / 1000.0 # kHz
    bw_khz = max(fh - (fl / 1000.0), 10.0)
    
    zin = (R1 * R2) / (R1 + R2)
    zout = RC
    p_loss = (VCC * IE) * 1000.0 # mW
    eff = min(45.0, (0.5 * (IE**2 * RC) / (VCC * IE)) * 100.0)

    metrics = [
        _metric('gain', 'Voltage Gain', 'dB', gain_db, 10.0, 50.0, 98.4, 
                "Small-signal voltage amplification ratio (20 log Av).", 
                "High small-signal voltage gain provided by CE stage.", "primary"),
        _metric('cgain', 'Current Gain', 'ratio', cgain, 20.0, 200.0, 97.9, 
                "Transistor AC current amplification factor (beta).", 
                "Standard BJT current gain level.", "info"),
        _metric('pgain', 'Power Gain', 'dB', pgain, 20.0, 80.0, 98.0, 
                "Product of voltage gain and current gain.", 
                "Substantial power gain for driving subsequent stages.", "purple"),
        _metric('bw', 'Bandwidth', 'kHz', bw_khz, 1.0, 50000.0, 97.2, 
                "Frequency band between lower (-3dB) and upper cutoff points.", 
                "Broad audio and IF frequency response.", "warning"),
        _metric('fl', 'Lower Cutoff Frequency', 'Hz', fl, 1.0, 1000.0, 98.1, 
                "Lower corner frequency set by input coupling capacitor C1.", 
                "Appropriate lower cutoff for audio signals.", "success"),
        _metric('fh', 'Upper Cutoff Frequency', 'kHz', fh, 100.0, 500000.0, 97.0, 
                "Upper corner frequency governed by parasitic capacitances.", 
                "Sufficiently high upper cutoff to prevent high-frequency distortion.", "secondary"),
        _metric('zin', 'Input Impedance', 'Ω', zin, 100.0, 100000.0, 98.5, 
                "Equivalent AC resistance seen by input signal source.", 
                "Moderate input impedance; consider buffer for high Z sources.", "info"),
        _metric('zout', 'Output Impedance', 'Ω', zout, 100.0, 50000.0, 98.8, 
                "Output resistance dominated by collector load resistor RC.", 
                "Matches typical medium-impedance loads.", "warning"),
        _metric('p_loss', 'Power Consumption', 'mW', p_loss, 1.0, 500.0, 99.0, 
                "Quiescent DC bias power dissipation.", 
                "Low power dissipation suitable for low-noise preamps.", "danger"),
        _metric('eff', 'Efficiency', '%', eff, 1.0, 50.0, 97.5, 
                "Ratio of AC signal load power to DC supply input power.", 
                "Typical Class-A stage efficiency (max theoretical 50%).", "success"),
    ]
    
    score = min(99.0, max(50.0, gain_db * 2.5 + 20.0))
    return {'metrics': metrics, 'score': round(score, 1)}


def _calc_common_collector(p):
    RB = float(p.get('RB', 100000))
    RE = float(p.get('RE', 1000))
    beta = 100.0
    re = 25.0
    
    gain_ratio = (beta * RE) / ((beta * RE) + RB + re)
    cgain = beta + 1.0
    zin_kohms = (RB * (beta * RE)) / (RB + (beta * RE)) / 1000.0
    zout_ohms = (re + (RB / beta))
    eff = 35.0

    metrics = [
        _metric('gain', 'Voltage Gain', 'V/V', gain_ratio, 0.8, 1.0, 99.2, 
                "Near-unity non-inverting voltage gain.", 
                "Ideal buffer characteristic with minimal voltage loss.", "primary"),
        _metric('cgain', 'Current Gain', 'ratio', cgain, 20.0, 300.0, 98.4, 
                "High AC current gain (β + 1).", 
                "Provides strong current amplification.", "purple"),
        _metric('zin', 'Input Impedance', 'kΩ', zin_kohms, 1.0, 500.0, 98.7, 
                "Very high input impedance minimizes loading on prior stage.", 
                "Excellent input impedance for buffer applications.", "info"),
        _metric('zout', 'Output Impedance', 'Ω', zout_ohms, 1.0, 500.0, 98.9, 
                "Low output impedance capable of driving heavy loads.", 
                "Low Zout enables impedance matching.", "warning"),
        _metric('eff', 'Efficiency', '%', eff, 5.0, 50.0, 97.0, 
                "Class-A emitter follower stage efficiency.", 
                "Standard power efficiency for linear buffer.", "success"),
    ]
    
    return {'metrics': metrics, 'score': 95.0}


def _calc_common_base(p):
    RB = float(p.get('RB', 10000))
    RC = float(p.get('RC', 3300))
    RE = float(p.get('RE', 500))
    re = 25.0
    
    Av_linear = RC / re
    gain_db = 20 * math.log10(max(Av_linear, 1.0))
    cgain = 0.99
    pgain = gain_db + 20 * math.log10(cgain)
    bw_mhz = 15.4
    zin = re
    zout = RC / 1000.0 # kΩ

    metrics = [
        _metric('gain', 'Voltage Gain', 'dB', gain_db, 10.0, 60.0, 98.3, 
                "High non-inverting voltage amplification.", 
                "Strong RF signal amplification.", "primary"),
        _metric('cgain', 'Current Gain', 'ratio', cgain, 0.9, 1.0, 99.5, 
                "Near-unity current gain (alpha).", 
                "Unity current gain prevents current amplification.", "info"),
        _metric('pgain', 'Power Gain', 'dB', pgain, 10.0, 50.0, 98.0, 
                "Net power gain delivered to load.", 
                "High power gain at high radio frequencies.", "purple"),
        _metric('bw', 'Bandwidth', 'MHz', bw_mhz, 1.0, 200.0, 97.6, 
                "Ultra-wide bandwidth due to absence of Miller effect.", 
                "Wide bandwidth ideal for RF preamplifiers.", "warning"),
        _metric('zin', 'Input Impedance', 'Ω', zin, 1.0, 100.0, 98.8, 
                "Low input impedance matching 50Ω antenna lines.", 
                "Perfect match for low impedance RF cables.", "secondary"),
        _metric('zout', 'Output Impedance', 'kΩ', zout, 0.5, 100.0, 98.5, 
                "High output impedance.", 
                "Suitable for driving subsequent high-Z stages.", "success"),
    ]
    
    return {'metrics': metrics, 'score': 94.0}


def _calc_inverting_opamp(p):
    Rin = float(p.get('Rin', 10000))
    Rf = float(p.get('Rf', 100000))
    
    ratio = Rf / Rin
    gain_db = 20 * math.log10(max(ratio, 0.001))
    gbw_khz = 10000.0 # 10 MHz op-amp GBW
    bw_khz = gbw_khz / max(ratio, 1.0)
    slew_rate = 10.0 # V/us
    vout = 1.0 * (-ratio) # Assume 1V input
    pm = 60.0

    metrics = [
        _metric('gain', 'Voltage Gain', 'dB', gain_db, 0.0, 60.0, 99.0, 
                "Closed-loop inverting voltage gain (-Rf / Rin).", 
                "Precise gain set by feedback resistor ratio.", "primary"),
        _metric('bw', 'Bandwidth', 'kHz', bw_khz, 1.0, 10000.0, 98.1, 
                "Closed-loop 3dB bandwidth based on Op-Amp Gain-Bandwidth product.", 
                "Bandwidth trade-off inversely proportional to gain.", "warning"),
        _metric('slew_rate', 'Slew Rate', 'V/µs', slew_rate, 0.5, 100.0, 98.8, 
                "Maximum rate of change of output voltage.", 
                "High slew rate prevents large-signal distortion.", "danger"),
        _metric('vout', 'Output Voltage', 'V', vout, -15.0, 15.0, 99.2, 
                "Inverted output voltage amplitude for 1V peak input.", 
                "Remains within power supply saturation limits.", "success"),
        _metric('pm', 'Phase Margin', '°', pm, 45.0, 90.0, 97.9, 
                "Op-Amp stability phase margin.", 
                "Solid stability margin prevents ringing.", "purple"),
    ]
    
    return {'metrics': metrics, 'score': 96.0}


def _calc_non_inverting_opamp(p):
    R1 = float(p.get('R1', 10000))
    R2 = float(p.get('R2', 90000))
    
    ratio = 1.0 + (R2 / R1)
    gain_db = 20 * math.log10(max(ratio, 1.0))
    gbw_khz = 10000.0
    bw_khz = gbw_khz / ratio
    pm = 65.0
    vout = 1.0 * ratio

    metrics = [
        _metric('gain', 'Voltage Gain', 'dB', gain_db, 0.0, 60.0, 99.1, 
                "Non-inverting gain formula 1 + (R2 / R1).", 
                "High precision non-inverting gain.", "primary"),
        _metric('bw', 'Bandwidth', 'kHz', bw_khz, 1.0, 10000.0, 98.0, 
                "Closed-loop bandwidth.", 
                "Consistent gain-bandwidth tradeoff.", "warning"),
        _metric('pm', 'Phase Margin', '°', pm, 45.0, 90.0, 98.5, 
                "Loop phase stability margin.", 
                "Excellent dynamic stability.", "purple"),
        _metric('vout', 'Output Voltage', 'V', vout, 0.0, 15.0, 99.3, 
                "In-phase output voltage for 1V input.", 
                "In-phase output with linear response.", "success"),
    ]
    
    return {'metrics': metrics, 'score': 96.5}


def _calc_differential_amp(p):
    R1 = float(p.get('R1', 10000))
    R2 = float(p.get('R2', 100000))
    R3 = float(p.get('R3', 10000))
    R4 = float(p.get('R4', 100000))
    
    Ad = R2 / R1
    Acm = abs((R1*R4 - R2*R3) / (R1*(R3 + R4)))
    cmrr_db = 20 * math.log10(max(Ad / max(Acm, 1e-6), 1.0))
    bw_khz = 100.0
    vos = 1.2 # mV

    metrics = [
        _metric('ad', 'Differential Gain', 'V/V', Ad, 1.0, 100.0, 98.9, 
                "Amplification factor for differential input signals (V2 - V1).", 
                "High differential signal amplification.", "primary"),
        _metric('acm', 'Common Mode Gain', 'V/V', Acm, 0.0, 1.0, 97.5, 
                "Gain for identical common-mode signals present on both inputs.", 
                "Near zero common mode gain rejects noise.", "warning"),
        _metric('cmrr', 'CMRR', 'dB', cmrr_db, 40.0, 120.0, 98.7, 
                "Common Mode Rejection Ratio measuring noise rejection performance.", 
                "High CMRR effectively suppresses unwanted interference.", "success"),
        _metric('bw', 'Bandwidth', 'kHz', bw_khz, 1.0, 1000.0, 97.9, 
                "Small signal differential bandwidth.", 
                "Sufficient bandwidth for industrial sensors.", "purple"),
        _metric('vos', 'Input Offset Voltage', 'mV', vos, 0.0, 10.0, 98.2, 
                "Input voltage mismatch leading to output offset voltage.", 
                "Low input offset voltage ensures high precision.", "danger"),
    ]
    
    return {'metrics': metrics, 'score': 95.5}


def _calc_instrumentation_amp(p):
    RG = float(p.get('RG', 1000))
    R1 = float(p.get('R1', 25000))
    R2 = float(p.get('R2', 10000))
    R3 = float(p.get('R3', 10000))
    
    gain1 = 1.0 + (2.0 * R1 / RG)
    gain2 = R3 / R2
    overall_gain = gain1 * gain2
    cmrr_db = 95.0 + (20 * math.log10(overall_gain / 10.0))
    bw_khz = 120.0
    vos = 0.25 # mV
    zin_mohm = 1000.0 # 1 Gohm

    metrics = [
        _metric('gain', 'Overall Gain', 'V/V', overall_gain, 1.0, 1000.0, 99.3, 
                "3-Op-Amp precision gain set by single resistor RG.", 
                "Adjustable high precision gain for sensor signals.", "primary"),
        _metric('cmrr', 'CMRR', 'dB', cmrr_db, 80.0, 140.0, 99.1, 
                "Extremely high rejection of common mode noise.", 
                "Biomedical grade CMRR rejects 50/60Hz mains interference.", "success"),
        _metric('bw', 'Bandwidth', 'kHz', bw_khz, 1.0, 1000.0, 97.8, 
                "Differential passband bandwidth.", 
                "Ideal bandwidth for strain gauge & ECG signals.", "warning"),
        _metric('vos', 'Offset Voltage', 'mV', vos, 0.0, 2.0, 98.6, 
                "Low initial input offset voltage.", 
                "Ultra-low offset voltage avoids calibration drift.", "danger"),
        _metric('zin', 'Input Impedance', 'MΩ', zin_mohm, 100.0, 10000.0, 99.5, 
                "Gigohm input impedance prevents loading sensitive transducers.", 
                "Ultra-high input impedance.", "info"),
    ]
    
    return {'metrics': metrics, 'score': 98.0}


def _calc_rc_oscillator(p):
    R = float(p.get('R', 10000))
    C = float(p.get('C', 0.01)) * 1e-6
    
    fo = 1.0 / (2 * math.pi * R * C * math.sqrt(6.0))
    vamp = 5.0
    pout = (vamp**2 / (2 * R)) * 1000.0 # mW
    freq_stability = 99.4 # %

    metrics = [
        _metric('fo', 'Oscillation Frequency', 'Hz', fo, 10, 100000, 98.4, 
                "Frequency of sustained sinusoidal oscillation (fo = 1 / (2πRC√6)).", 
                "Stable audio frequency sine wave output.", "success"),
        _metric('vamp', 'Output Amplitude', 'V', vamp, 1.0, 12.0, 99.0, 
                "Peak-to-peak output AC voltage amplitude.", 
                "Clean sine wave amplitude suitable for tone generation.", "primary"),
        _metric('pout', 'Output Power', 'mW', pout, 0.1, 100.0, 97.6, 
                "AC power delivered by oscillator stage.", 
                "Low distortion oscillator output power.", "purple"),
        _metric('freq_stability', 'Frequency Stability', '%', freq_stability, 90.0, 100.0, 98.8, 
                "Percentage stability against component thermal drift.", 
                "High frequency stability for audio testing.", "info"),
    ]
    
    return {'metrics': metrics, 'score': 93.0}


def _calc_rectifier(p):
    RL = float(p.get('RL', 1000))
    Vin_rms = float(p.get('Vin', 12.0))
    C = 1000e-6
    f = 50.0
    
    Vpeak = Vin_rms * math.sqrt(2) - 1.4
    Idc = Vpeak / RL
    Vripple = Idc / (2 * f * C)
    Vdc = Vpeak - (Vripple / 2.0)
    rf = Vripple / Vdc
    p_loss = 1.4 * Idc # W
    eff = min(95.0, max(40.0, (Vdc * Idc) / ((Vin_rms * Idc) + p_loss) * 100.0))

    metrics = [
        _metric('vdc', 'Output Voltage', 'V', Vdc, 1.0, 500.0, 98.8, 
                "Filtered DC output voltage after full-wave bridge rectification.", 
                "Stable DC rail voltage.", "success"),
        _metric('vripple', 'Ripple Voltage', 'V', Vripple, 0.01, 5.0, 97.9, 
                "Peak-to-peak AC ripple superimposed on DC rail.", 
                "Keep ripple voltage low by choosing larger C.", "danger"),
        _metric('rf', 'Ripple Factor', 'ratio', rf, 0.001, 0.1, 98.2, 
                "Ratio of RMS ripple voltage to average DC output voltage.", 
                "Low ripple factor indicates clean DC power.", "warning"),
        _metric('eff', 'Efficiency', '%', eff, 50.0, 98.0, 98.5, 
                "Conversion efficiency of AC input power to DC load power.", 
                "High power conversion efficiency.", "primary"),
        _metric('p_loss', 'Power Loss', 'W', p_loss, 0.01, 20.0, 98.9, 
                "Power dissipated across diode bridge forward voltage drops.", 
                "Minimal diode conduction power loss.", "purple"),
        _metric('idc', 'Output Current', 'A', Idc, 0.001, 10.0, 99.1, 
                "Continuous DC load current supplied.", 
                "Sufficient current capacity for linear regulator input.", "info"),
    ]
    
    return {'metrics': metrics, 'score': round(eff, 1)}


def _calc_buck_converter(p):
    L = float(p.get('L', 1.0)) * 1e-3
    C = float(p.get('C', 100.0)) * 1e-6
    D = float(p.get('D', 50.0)) / 100.0
    Vin = float(p.get('Vin', 24.0))
    fsw = 100000.0
    RL = 10.0 # Ω load
    
    Vout = D * Vin
    Iout = Vout / RL
    Vripple_mv = (Vin * D * (1.0 - D)) / (8.0 * L * C * (fsw**2)) * 1000.0
    Iripple = (Vin - Vout) * D / (fsw * L)
    P_out = Vout * Iout
    eff = max(60.0, 94.0 - (D * 3.0) - (Iout * 0.5))
    P_loss = P_out * ((100.0 - eff) / eff)

    metrics = [
        _metric('vout', 'Output Voltage', 'V', Vout, 1.0, 250.0, 99.0, 
                "Regulated step-down output voltage (Vout = D * Vin).", 
                "Accurate step-down voltage control.", "success"),
        _metric('iout', 'Output Current', 'A', Iout, 0.1, 50.0, 98.5, 
                "Delivered load current.", 
                "High output current capability.", "info"),
        _metric('vripple', 'Ripple Voltage', 'mV', Vripple_mv, 1.0, 500.0, 97.8, 
                "High-frequency switching voltage ripple.", 
                "Low voltage ripple protects sensitive digital ICs.", "danger"),
        _metric('iripple', 'Ripple Current', 'A', Iripple, 0.01, 5.0, 98.1, 
                "Inductor peak-to-peak ripple current.", 
                "Keep ripple current below 30% of average load current.", "warning"),
        _metric('eff', 'Efficiency', '%', eff, 70.0, 98.0, 98.9, 
                "Switching power conversion efficiency.", 
                "High efficiency reduces thermal heatsink requirements.", "primary"),
        _metric('duty', 'Duty Cycle', '%', D * 100.0, 5.0, 95.0, 99.5, 
                "PWM switching duty cycle percentage.", 
                "Optimal PWM duty cycle range.", "secondary"),
        _metric('p_loss', 'Power Loss', 'W', P_loss, 0.05, 50.0, 98.4, 
                "Combined switching and conduction power losses.", 
                "Low thermal power loss.", "purple"),
        _metric('p_out', 'Output Power', 'W', P_out, 0.1, 500.0, 99.2, 
                "Total electrical power delivered to output load.", 
                "Robust power delivery capability.", "success"),
    ]
    
    return {'metrics': metrics, 'score': round(eff, 1)}


def _calc_boost_converter(p):
    L = float(p.get('L', 0.5)) * 1e-3
    C = float(p.get('C', 220.0)) * 1e-6
    D = float(p.get('D', 60.0)) / 100.0
    Vin = float(p.get('Vin', 12.0))
    fsw = 100000.0
    RL = 20.0
    
    D_clamped = min(D, 0.9)
    Vout = Vin / (1.0 - D_clamped)
    Iout = Vout / RL
    Vripple_mv = (Iout * D_clamped) / (fsw * C) * 1000.0
    Iripple = (Vin * D_clamped) / (fsw * L)
    P_out = Vout * Iout
    eff = max(50.0, 91.0 - (D_clamped * 4.0) - (Iout * 0.8))
    P_loss = P_out * ((100.0 - eff) / eff)

    metrics = [
        _metric('vout', 'Output Voltage', 'V', Vout, 1.0, 500.0, 98.8, 
                "Stepped-up DC output voltage (Vout = Vin / (1 - D)).", 
                "High output DC step-up ratio.", "success"),
        _metric('iout', 'Output Current', 'A', Iout, 0.05, 20.0, 98.3, 
                "Output load current.", 
                "Continuous DC load current delivery.", "info"),
        _metric('vripple', 'Ripple Voltage', 'mV', Vripple_mv, 1.0, 1000.0, 97.6, 
                "Output capacitor switching voltage ripple.", 
                "Increase C to reduce ripple voltage.", "danger"),
        _metric('iripple', 'Ripple Current', 'A', Iripple, 0.05, 10.0, 98.0, 
                "Inductor current ripple amplitude.", 
                "Controlled inductor ripple current.", "warning"),
        _metric('eff', 'Efficiency', '%', eff, 65.0, 96.0, 98.7, 
                "Boost power conversion efficiency.", 
                "High efficiency for battery boost applications.", "primary"),
        _metric('duty', 'Duty Cycle', '%', D_clamped * 100.0, 5.0, 85.0, 99.4, 
                "PWM gate duty cycle percentage.", 
                "Avoid duty cycles above 85% to prevent instability.", "secondary"),
        _metric('p_loss', 'Power Loss', 'W', P_loss, 0.1, 50.0, 98.2, 
                "Switching transistor and diode conduction losses.", 
                "Low thermal losses.", "purple"),
        _metric('p_out', 'Output Power', 'W', P_out, 0.1, 500.0, 99.1, 
                "Total output power supplied.", 
                "Strong output power rating.", "success"),
    ]
    
    return {'metrics': metrics, 'score': round(eff, 1)}


def get_circuit_config(slug):
    """Retrieve circuit configuration dictionary by slug."""
    return CIRCUIT_REGISTRY.get(slug, None)


def get_circuits_by_category():
    """Group all 15 circuits into 5 categories."""
    categories = {
        'filters': {'name': 'Filters', 'icon': 'bi-funnel-fill', 'circuits': []},
        'amplifiers': {'name': 'Amplifiers', 'icon': 'bi-diagram-3-fill', 'circuits': []},
        'oscillators': {'name': 'Oscillators', 'icon': 'bi-sinewave', 'circuits': []},
        'rectifiers': {'name': 'Rectifiers', 'icon': 'bi-lightning-charge-fill', 'circuits': []},
        'converters': {'name': 'DC-DC Converters', 'icon': 'bi-cpu-fill', 'circuits': []},
    }
    
    for slug, config in CIRCUIT_REGISTRY.items():
        cat_key = config['category_slug']
        if cat_key in categories:
            categories[cat_key]['circuits'].append(config)
            
    return categories
