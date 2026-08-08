"""
ai_assistant.py
CircuitAI - AI Chat Assistant Module
Intelligent domain assistant for electronic engineering, circuit design, metric explanations,
troubleshooting predicted values, and component recommendations.
"""

def generate_bot_response(user_query, active_circuit_slug=None, active_prediction_data=None):
    """
    Generate domain-specific intelligent responses to user queries.
    Uses query intent matching + active circuit context.
    """
    query = user_query.strip().lower()

    # Question 1: Common Emitter Amplifier
    if "common emitter" in query or "ce amplifier" in query:
        return {
            'reply': (
                "**Common Emitter (CE) Amplifier Overview**\n\n"
                "A Common Emitter Amplifier is the most widely used BJT transistor amplifier configuration. "
                "The emitter terminal is common to both the input and output circuits (often connected to ground or a bypassed resistor).\n\n"
                "**Key Characteristics:**\n"
                "• **High Voltage Gain:** Typically 20 dB to 50 dB.\n"
                "• **High Power Gain:** Amplifies both voltage and current.\n"
                "• **180° Phase Inversion:** Output voltage waveform is inverted relative to the input signal.\n"
                "• **Moderate Input/Output Impedance:** Zin ~ 1 kΩ to 10 kΩ, Zout ~ RC.\n\n"
                "**Common Applications:** Audio preamplifiers, voltage gain stages, and small-signal analog sensors."
            )
        }

    # Question 2: How to increase Gain
    if "increase gain" in query or "raise gain" in query or "higher gain" in query:
        return {
            'reply': (
                "**How to Increase Circuit Voltage Gain:**\n\n"
                "1. **BJT Amplifiers (Common Emitter):**\n"
                "   • Increase Collector Resistance ($R_C$).\n"
                "   • Add or increase the Emitter Bypass Capacitor ($C_E$) to bypass $R_E$ for AC signals, reducing internal AC emitter degradation ($r_e$).\n"
                "   • Increase quiescent collector bias current ($I_C$).\n\n"
                "2. **Op-Amp Circuits:**\n"
                "   • **Inverting Op-Amp:** Increase Feedback Resistor ($R_f$) or decrease Input Resistor ($R_{in}$) [$A_v = -R_f / R_{in}$].\n"
                "   • **Non-Inverting Op-Amp:** Increase Feedback Resistor ($R_2$) relative to Ground Resistor ($R_1$) [$A_v = 1 + R_2 / R_1$].\n\n"
                "3. **Instrumentation Amplifiers:**\n"
                "   • Decrease the Gain Setting Resistor ($R_G$) [$Gain = 1 + (2 R_1 / R_G)$]."
            )
        }

    # Question 3: What does Cutoff Frequency mean
    if "cutoff frequency" in query or "what is fc" in query or "cut off" in query:
        return {
            'reply': (
                "**Understanding Cutoff Frequency ($f_c$):**\n\n"
                "The Cutoff Frequency ($f_c$), also known as corner or half-power frequency, is the boundary point in a circuit's frequency response where the output signal power drops to **50% of peak power**.\n\n"
                "**Key Facts:**\n"
                "• **Voltage Drop:** Voltage gain drops by **-3.01 dB** (or to $1/\sqrt{2} \approx 0.707$ of its passband value).\n"
                "• **Phase Shift:** Exactly **45° phase shift** occurs at $f_c$ in 1st-order RC filters.\n"
                "• **Formula for RC Filter:** $f_c = \\frac{1}{2 \\pi R C}$.\n\n"
                "In low-pass filters, frequencies above $f_c$ are attenuated. In high-pass filters, frequencies below $f_c$ are blocked."
            )
        }

    # Question 4: Why is my predicted gain low
    if "predicted gain low" in query or "gain is low" in query or "why is gain low" in query:
        context_msg = ""
        if active_prediction_data and 'inputs_used' in active_prediction_data:
            inputs = active_prediction_data['inputs_used']
            context_msg = f" (Current inputs: {inputs})"
            
        return {
            'reply': (
                "**Reasons Your Predicted Gain Might Be Low:**\n\n"
                "1. **Impedance Loading / High Input Resistance:** If $R_{in}$ or source impedance is too high relative to feedback resistors, gain drops.\n"
                "2. **Excessive Emitter Degeneration:** In BJT stages, an unbypassed Emitter Resistor ($R_E$) stabilizes bias but severely lowers AC voltage gain ($A_v \\approx R_C / R_E$).\n"
                "3. **Op-Amp Gain-Bandwidth Product (GBW) Limits:** At high frequencies, closed-loop op-amp gain rolls off at -20 dB/decade.\n"
                "4. **Low Collector Load Resistance ($R_C$):** In CE amplifiers, small $R_C$ reduces output voltage swing.\n\n"
                "**Actionable Fix:** Try increasing feedback resistance ($R_f$ or $R_C$) or run our **AI Circuit Optimizer** tab to auto-calculate ideal values!" + context_msg
            )
        }

    # Question 5: Which circuit is best for high bandwidth
    if "high bandwidth" in query or "best for bandwidth" in query or "widest bandwidth" in query:
        return {
            'reply': (
                "**Best Circuits for High Bandwidth Applications:**\n\n"
                "1. **Common Base (CB) Amplifier:** **[TOP CHOICE FOR RF]**\n"
                "   • Eliminates the Miller effect capacity boost between input and output.\n"
                "   • Offers bandwidths in tens to hundreds of MHz!\n\n"
                "2. **Common Collector (Emitter Follower):**\n"
                "   • Near unity voltage gain provides wide bandwidth and low output impedance for high-speed buffering.\n\n"
                "3. **Low-Gain Op-Amp Stages:**\n"
                "   • Operating op-amps with lower closed-loop gain maximizes available bandwidth due to constant Gain-Bandwidth Product (GBW)."
            )
        }

    # Circuit Explanations
    if "common collector" in query or "emitter follower" in query:
        return {'reply': "The Common Collector (Emitter Follower) provides high input impedance, low output impedance, and near-unity voltage gain. Ideal for impedance buffering."}

    if "common base" in query:
        return {'reply': "The Common Base configuration features low input impedance, high output impedance, and high voltage gain without Miller multiplication. Best for RF high-frequency preamps."}

    if "op-amp" in query or "operational amplifier" in query:
        return {'reply': "Operational Amplifiers (Op-Amps) are high-gain differential voltage amplifiers used in inverting, non-inverting, differential, and active filter topologies."}

    if "buck converter" in query or "boost converter" in query:
        return {'reply': "Buck Converters step down DC voltage efficiently using PWM switching, while Boost Converters step up DC voltage. Efficiency typically ranges from 85% to 96%."}

    if "rectifier" in query or "ripple" in query:
        return {'reply': "Rectifiers convert AC signals to DC. The smoothing capacitor filters AC ripple voltage. Larger capacitor values lower ripple voltage and improve DC purity."}

    if "active filter" in query or "sallen-key" in query:
        return {'reply': "Active filters combine op-amps with resistors and capacitors to achieve sharp frequency roll-off, controlled Q-factor, and passband amplification without inductors."}

    if "oscillator" in query or "rc phase shift" in query:
        return {'reply': "RC Phase Shift Oscillators use 3-stage RC feedback networks providing 180° phase shift combined with an inverting amplifier to produce stable sine wave oscillations."}

    # Default Contextual Response
    active_str = f" for **{active_circuit_slug}**" if active_circuit_slug else ""
    return {
        'reply': (
            f"**CircuitAI Engineering Assistant Response:**\n\n"
            f"I have analyzed your query: *\"{user_query}\"*{active_str}.\n\n"
            "Here are relevant engineering Insights:\n"
            "• **Circuit Dynamics:** Component values (R, C, L) directly govern transfer functions, corner frequencies, and impedance matching.\n"
            "• **Optimization:** Use our **AI Circuit Optimizer** tool to calculate standard E24 component values for target specifications.\n"
            "• **Simulation:** Adjust input parameters in the left panel to update real-time vector schematics and multi-output metrics."
        )
    }
