"""
decoder.py
Implements waveform parameter-based decoders and descramblers:
- Line Coding Decoders: NRZ-L, NRZ-I, Manchester, Differential Manchester, AMI
- Scrambling Decoders / Descramblers: B8ZS and HDB3 (Violation detection)

All decoders reconstruct the original digital bitstream strictly from physical
voltage levels, timing boundaries, and signal transitions without reading
source bit values.
"""

import numpy as np


def _get_bit_intervals(time: np.ndarray, voltage: np.ndarray, num_bits: int = None):
    """
    Helper function to calculate the number of bit intervals and samples per bit
    from physical continuous time and voltage arrays.
    """
    total_samples = len(voltage)
    if num_bits is None:
        duration = float(time[-1]) if len(time) > 0 else 0.0
        num_bits = int(round(duration))
    
    if num_bits <= 0:
        return 0, 0

    samples_per_bit = total_samples // num_bits
    return num_bits, samples_per_bit


def decode_nrz_l(time: np.ndarray, voltage: np.ndarray, num_bits: int = None) -> str:
    """
    Decodes NRZ-L signal by sampling the voltage level within each bit interval.
    - Positive voltage (> 0V) -> Bit '0'
    - Negative voltage (< 0V) -> Bit '1'
    """
    num_bits, spb = _get_bit_intervals(time, voltage, num_bits)
    decoded_bits = []

    for k in range(num_bits):
        # Sample near the center of the bit duration to avoid boundary jitter
        center_idx = k * spb + (spb // 2)
        v_sample = voltage[center_idx]
        decoded_bits.append('0' if v_sample > 0 else '1')

    return "".join(decoded_bits)


def decode_nrz_i(time: np.ndarray, voltage: np.ndarray, num_bits: int = None, 
                 initial_level: int = 1) -> str:
    """
    Decodes NRZ-I signal by detecting presence or absence of a voltage transition
    at the start of each bit interval.
    - Voltage inversion from previous bit level -> Bit '1'
    - No transition from previous bit level     -> Bit '0'
    """
    num_bits, spb = _get_bit_intervals(time, voltage, num_bits)
    decoded_bits = []
    prev_level = initial_level

    for k in range(num_bits):
        center_idx = k * spb + (spb // 2)
        curr_level = 1 if voltage[center_idx] > 0 else -1

        # In NRZ-I, a level change indicates '1', unchanged level indicates '0'
        if curr_level != prev_level:
            decoded_bits.append('1')
        else:
            decoded_bits.append('0')

        prev_level = curr_level

    return "".join(decoded_bits)


def decode_manchester(time: np.ndarray, voltage: np.ndarray, num_bits: int = None) -> str:
    """
    Decodes Manchester signal (IEEE 802.3 convention) by inspecting the direction
    of the mid-bit transition.
    - High to Low (+1V to -1V) -> Bit '0'
    - Low to High (-1V to +1V) -> Bit '1'
    """
    num_bits, spb = _get_bit_intervals(time, voltage, num_bits)
    decoded_bits = []

    for k in range(num_bits):
        # Sample in first half (25% point) and second half (75% point)
        first_half_sample = voltage[k * spb + (spb // 4)]
        second_half_sample = voltage[k * spb + (3 * spb // 4)]

        if first_half_sample > 0 and second_half_sample < 0:
            decoded_bits.append('0')
        elif first_half_sample < 0 and second_half_sample > 0:
            decoded_bits.append('1')
        else:
            # Fallback based on mid-interval comparison
            decoded_bits.append('0' if first_half_sample > second_half_sample else '1')

    return "".join(decoded_bits)


def decode_diff_manchester(time: np.ndarray, voltage: np.ndarray, num_bits: int = None,
                           initial_level: int = 1) -> str:
    """
    Decodes Differential Manchester signal:
    - Transition at the beginning of the bit interval -> Bit '0'
    - No transition at the beginning of the bit interval -> Bit '1'
    (Mid-bit transition is present in all bits for clock sync).
    """
    num_bits, spb = _get_bit_intervals(time, voltage, num_bits)
    decoded_bits = []
    prev_second_half = initial_level

    for k in range(num_bits):
        first_half_sample = 1 if voltage[k * spb + (spb // 4)] > 0 else -1
        second_half_sample = 1 if voltage[k * spb + (3 * spb // 4)] > 0 else -1

        # Check if a transition occurred at the boundary between previous bit's end
        # and current bit's start
        if first_half_sample != prev_second_half:
            decoded_bits.append('0')
        else:
            decoded_bits.append('1')

        prev_second_half = second_half_sample

    return "".join(decoded_bits)


def decode_ami(time: np.ndarray, voltage: np.ndarray, num_bits: int = None) -> str:
    """
    Decodes Alternate Mark Inversion (AMI) signal:
    - 0V level              -> Bit '0'
    - Non-zero (+1V or -1V) -> Bit '1'
    """
    num_bits, spb = _get_bit_intervals(time, voltage, num_bits)
    decoded_bits = []

    for k in range(num_bits):
        center_idx = k * spb + (spb // 2)
        v = voltage[center_idx]
        if abs(v) < 0.5:
            decoded_bits.append('0')
        else:
            decoded_bits.append('1')

    return "".join(decoded_bits)


def extract_discrete_levels(time: np.ndarray, voltage: np.ndarray, num_bits: int = None) -> list:
    """
    Samples physical continuous waveform to discrete ternary voltage levels [-1, 0, +1].
    Useful for feeding into AMI descramblers.
    """
    num_bits, spb = _get_bit_intervals(time, voltage, num_bits)
    levels = []

    for k in range(num_bits):
        v = voltage[k * spb + (spb // 2)]
        if abs(v) < 0.3:
            levels.append(0)
        elif v > 0:
            levels.append(1)
        else:
            levels.append(-1)

    return levels


def descramble_b8zs(levels: list) -> str:
    """
    Descrambles B8ZS encoded discrete ternary levels back to the original bitstream.
    Detects the 8-symbol substitution pattern: 0 0 0 V B 0 V B
    where V is a Bipolar Violation (same polarity as last pulse).
    """
    decoded = []
    i = 0
    n = len(levels)
    last_polarity = -1

    while i < n:
        # Check if an 8-symbol sequence matches B8ZS violation pattern
        if i + 8 <= n:
            sub = levels[i:i + 8]
            # Pattern check: 0 0 0 V B 0 V B
            # Indices 0, 1, 2, 5 must be 0
            # Indices 3, 4, 6, 7 must be non-zero pulses with B8ZS alternating relations
            if (sub[0] == 0 and sub[1] == 0 and sub[2] == 0 and sub[5] == 0 and
                sub[3] != 0 and sub[4] == -sub[3] and sub[6] == sub[4] and sub[7] == -sub[6]):
                
                # Check if sub[3] violates AMI rule (same sign as last non-zero pulse)
                if sub[3] == last_polarity:
                    decoded.extend(['0'] * 8)
                    last_polarity = sub[7]
                    i += 8
                    continue

        lvl = levels[i]
        if lvl == 0:
            decoded.append('0')
        else:
            decoded.append('1')
            last_polarity = lvl
        i += 1

    return "".join(decoded)


def descramble_hdb3(levels: list) -> str:
    """
    Descrambles HDB3 encoded discrete ternary levels back to the original bitstream.
    Detects 4-symbol substitution patterns:
    - 0 0 0 V (Odd pulses since last substitution)
    - B 0 0 V (Even pulses since last substitution)
    where V has the SAME polarity as the immediately preceding non-zero pulse (Violation).
    """
    decoded = []
    n = len(levels)
    last_pulse_polarity = 0
    i = 0

    while i < n:
        lvl = levels[i]
        if lvl == 0:
            decoded.append('0')
            i += 1
        else:
            # Check if this non-zero pulse is a Bipolar Violation (V)
            # In AMI, legitimate consecutive pulses MUST alternate signs (+1 -> -1 or -1 -> +1).
            # If current pulse has same sign as previous pulse, it is a Violation!
            if last_pulse_polarity != 0 and lvl == last_pulse_polarity:
                # Violation detected at index i!
                # Check preceding 3 symbols in the decoded stream
                # Case 1: 000V pattern (preceding 3 levels were all 0)
                if i >= 3 and levels[i-1] == 0 and levels[i-2] == 0 and levels[i-3] == 0:
                    # Replace last 3 decoded bits and this one with '0000'
                    decoded[-3:] = ['0', '0', '0']
                    decoded.append('0')
                # Case 2: B00V pattern (preceding 3 levels were B, 0, 0 where B was balancing pulse)
                elif i >= 3 and levels[i-1] == 0 and levels[i-2] == 0 and levels[i-3] != 0:
                    # The pulse at i-3 was a balancing pulse (B), not true data 1
                    decoded[-3:] = ['0', '0', '0']
                    decoded.append('0')
                else:
                    decoded.append('0')

                last_pulse_polarity = lvl
                i += 1
            else:
                # Normal alternating AMI pulse -> Represents bit '1'
                decoded.append('1')
                last_pulse_polarity = lvl
                i += 1

    return "".join(decoded)


def decode_signal(time: np.ndarray, voltage: np.ndarray, scheme: str, 
                  initial_level: int = 1, num_bits: int = None) -> str:
    """
    Unified dispatcher to decode digital signals and scrambled waveforms.
    Supported schemes:
    - Line Codes: 'NRZ-L', 'NRZ-I', 'Manchester', 'Differential Manchester', 'AMI'
    - Scrambled AMI: 'B8ZS', 'HDB3'
    """
    normalized = scheme.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    if normalized == "nrzl":
        return decode_nrz_l(time, voltage, num_bits)
    elif normalized == "nrzi":
        return decode_nrz_i(time, voltage, num_bits, initial_level)
    elif normalized == "manchester":
        return decode_manchester(time, voltage, num_bits)
    elif normalized in ("differentialmanchester", "diffmanchester"):
        return decode_diff_manchester(time, voltage, num_bits, initial_level)
    elif normalized == "ami":
        return decode_ami(time, voltage, num_bits)
    elif normalized == "b8zs":
        levels = extract_discrete_levels(time, voltage, num_bits)
        return descramble_b8zs(levels)
    elif normalized == "hdb3":
        levels = extract_discrete_levels(time, voltage, num_bits)
        return descramble_hdb3(levels)
    else:
        raise ValueError(f"Unknown decoding scheme: {scheme}")


# ^^^^^^^^ Test ke liye likha hai maine (START) ^^^^^^^^
# (Yeh section sirf is file ko akele chala kar check karne ke liye hai, main project logic upar hai)
if __name__ == "__main__":
    from line_coding import encode_signal
    from scrambling import scramble_b8zs, scramble_hdb3

    print("--- Digital Signal & Scrambling Decoders Verification ---")

    # 1. Test all 5 standard line coding decoders
    test_stream = "101100101"
    schemes = ["NRZ-L", "NRZ-I", "Manchester", "Differential Manchester", "AMI"]

    print(f"\nOriginal Bitstream: {test_stream}")
    print("-" * 55)

    all_passed = True
    for scheme in schemes:
        levels, t, v = encode_signal(test_stream, scheme)
        decoded = decode_signal(t, v, scheme)
        status = "MATCH" if decoded == test_stream else "MISMATCH"
        if status != "MATCH":
            all_passed = False
        print(f"[{scheme:23s}] Decoded: {decoded} -> {status}")

    # 2. Test B8ZS Scrambler & Descrambler roundtrip
    print("\n--- B8ZS Scrambling & Descrambling Verification ---")
    b8zs_stream = "110000000010"
    b8zs_levels, b8zs_syms, t_b8zs, v_b8zs = scramble_b8zs(b8zs_stream)
    decoded_b8zs = decode_signal(t_b8zs, v_b8zs, "B8ZS")
    b8zs_status = "MATCH" if decoded_b8zs == b8zs_stream else "MISMATCH"
    if b8zs_status != "MATCH":
        all_passed = False
    print(f"Original B8ZS Stream : {b8zs_stream}")
    print(f"Scrambled Symbols    : {' '.join(b8zs_syms)}")
    print(f"Descrambled Bitstream: {decoded_b8zs} -> {b8zs_status}")

    # 3. Test HDB3 Scrambler & Descrambler roundtrip (both Odd and Even substitutions)
    print("\n--- HDB3 Scrambling & Descrambling Verification ---")
    hdb3_stream = "10000110000"
    hdb3_levels, hdb3_syms, t_hdb3, v_hdb3 = scramble_hdb3(hdb3_stream)
    decoded_hdb3 = decode_signal(t_hdb3, v_hdb3, "HDB3")
    hdb3_status = "MATCH" if decoded_hdb3 == hdb3_stream else "MISMATCH"
    if hdb3_status != "MATCH":
        all_passed = False
    print(f"Original HDB3 Stream : {hdb3_stream}")
    print(f"Scrambled Symbols    : {' '.join(hdb3_syms)}")
    print(f"Descrambled Bitstream: {decoded_hdb3} -> {hdb3_status}")

    print("-" * 55)
    if all_passed:
        print("All line coding decoders and descramblers verified successfully!")
    else:
        print("Some decoders had mismatches. Please check.")
# ^^^^^^^^ Test ke liye likha hai maine (END) ^^^^^^^^
