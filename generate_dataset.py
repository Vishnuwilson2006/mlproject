"""
generate_dataset.py
Synthetic Dataset Generation for ECE Final Year Project:
"Machine Learning-Based Surrogate Model for Circuit Performance Prediction"

Generates 12,000 samples of realistic circuit performance metrics based on
physics-grounded circuit equations (Common Emitter / Transistor Amplifier Stage).
"""

import numpy as np
import pandas as pd

def generate_circuit_dataset(n_samples=12000, random_seed=42):
    np.random.seed(random_seed)
    
    # 1. Generate Realistic Input Features
    # R1: Upper base biasing resistor (10 kOhm to 100 kOhm) -> 10,000 to 100,000 Ohms
    R1 = np.random.uniform(10000, 100000, n_samples)
    
    # R2: Lower base biasing resistor (1 kOhm to 25 kOhm) -> 1,000 to 25,000 Ohms
    R2 = np.random.uniform(1000, 25000, n_samples)
    
    # RC: Collector load resistor (500 Ohm to 10 kOhm) -> 500 to 10,000 Ohms
    RC = np.random.uniform(500, 10000, n_samples)
    
    # RE: Emitter stabilization resistor (50 Ohm to 2 kOhm) -> 50 to 2,000 Ohms
    RE = np.random.uniform(50, 2000, n_samples)
    
    # C1: Input coupling capacitor (0.1 uF to 10 uF) -> in uF
    C1 = np.random.uniform(0.1, 10.0, n_samples)
    
    # C2: Output coupling capacitor (0.1 uF to 10 uF) -> in uF
    C2 = np.random.uniform(0.1, 10.0, n_samples)
    
    # 2. Physics-Based Circuit Equations for Target Labels
    # Supply Voltage VCC = 12V
    VCC = 12.0
    
    # Base Voltage VB = VCC * (R2 / (R1 + R2))
    VB = VCC * (R2 / (R1 + R2))
    
    # Emitter Voltage VE = max(VB - 0.7, 0.1)
    VE = np.maximum(VB - 0.7, 0.1)
    
    # Emitter Current IE = VE / RE (Amperes)
    IE = VE / RE
    
    # Small-signal Emitter Resistance re = thermal voltage Vt / IE (Vt = 26mV)
    re = 0.026 / np.maximum(IE, 1e-5)
    
    # Voltage Gain Av = RC / (re + RE)
    Av_linear = RC / (re + RE)
    
    # Voltage Gain in dB: Gain_dB = 20 * log10(Av_linear)
    # Add minor component non-linearity & physical noise (1-2%)
    noise_gain = np.random.normal(0, 0.5, n_samples)
    Gain_dB = 20 * np.log10(np.maximum(Av_linear, 1.0)) + noise_gain
    Gain_dB = np.clip(Gain_dB, 5.0, 60.0) # Realistic range 5 dB to 60 dB
    
    # Cutoff Frequency (Hz): f_c ~ 1 / (2 * pi * Req * C_total)
    # Req ~ R1 || R2 + Rin_base (approx ~ R2 + 500)
    Req1 = (R1 * R2) / (R1 + R2)
    C1_farad = C1 * 1e-6
    C2_farad = C2 * 1e-6
    
    # Cutoff frequency dominates around low frequency corner
    fc_hz = 1.0 / (2 * np.pi * Req1 * C1_farad + 2 * np.pi * RC * C2_farad)
    noise_fc = np.random.normal(1.0, 0.03, n_samples)
    Cutoff_Frequency = fc_hz * noise_fc
    Cutoff_Frequency = np.clip(Cutoff_Frequency, 10.0, 100000.0) # 10 Hz to 100 kHz
    
    # Phase Margin (Degrees): PM = 180 - arctan(f / fp1) - arctan(f / fp2)
    # Typically varies between 45 to 90 degrees based on C1, C2 ratio and RC
    ratio = (C1 / C2) + (RC / (RE + 1e-3)) * 0.05
    pm_base = 90.0 - (15.0 * np.arctan(ratio - 1.0))
    noise_pm = np.random.normal(0, 1.2, n_samples)
    Phase_Margin = pm_base + noise_pm
    Phase_Margin = np.clip(Phase_Margin, 30.0, 90.0) # 30 to 90 degrees
    
    # 3. Create DataFrame
    df = pd.DataFrame({
        'R1': np.round(R1, 2),
        'R2': np.round(R2, 2),
        'RC': np.round(RC, 2),
        'RE': np.round(RE, 2),
        'C1': np.round(C1, 3),
        'C2': np.round(C2, 3),
        'Gain': np.round(Gain_dB, 2),
        'Cutoff_Frequency': np.round(Cutoff_Frequency, 2),
        'Phase_Margin': np.round(Phase_Margin, 2)
    })
    
    return df

if __name__ == "__main__":
    print("Generating synthetic circuit dataset (12,000 samples)...")
    dataset = generate_circuit_dataset(n_samples=12000)
    output_filename = "circuit_dataset.csv"
    dataset.to_csv(output_filename, index=False)
    print(f"Dataset successfully generated and saved to '{output_filename}'.")
    print(f"Shape: {dataset.shape}")
    print("\nDataset Sample:")
    print(dataset.head())
