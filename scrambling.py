"""
scrambling.py
Implements AMI Scrambling Schemes:
- B8ZS (Bipolar with 8-Zero Substitution)
- HDB3 (High-Density Bipolar 3-Zero)

Also includes an optimal O(N) zero-run detection algorithm for competitive
coding requirements, avoiding massive nested if-else statements.
"""

import numpy as np


def find_longest_zero_run(bitstream: str) -> dict:
    """
    Finds the longest contiguous sequence of zeros in the bitstream in O(N) linear time.
    
    Returns:
        dict: {'length': int, 'start_index': int, 'end_index': int}
    """
    max_len = 0
    curr_len = 0
    best_start = -1
    curr_start = -1

    for i, bit in enumerate(bitstream):
        if bit == '0':
            if curr_len == 0:
                curr_start = i
            curr_len += 1
            if curr_len > max_len:
                max_len = curr_len
                best_start = curr_start
        else:
            curr_len = 0

    best_end = (best_start + max_len) if best_start != -1 else -1
    return {
        "length": max_len,
        "start_index": best_start,
        "end_index": best_end
    }


def scramble_b8zs(bitstream: str, initial_polarity: int = -1):
    """
    B8ZS (Bipolar with 8-Zero Substitution):
    Replaces any run of 8 consecutive zeros ('00000000') with '000VB0VB'.
    - V: Bipolar Violation (same polarity as previous non-zero pulse)
    - B: Bipolar Balancing pulse (opposite polarity to previous pulse)
    
    Returns:
        tuple: (levels, symbols, time, voltage)
    """
    levels = []
    symbols = []
    last_polarity = initial_polarity  # Polarity of last non-zero pulse (+1 or -1)
    
    i = 0
    n = len(bitstream)
    
    while i < n:
        # Check if 8 consecutive zeros occur starting at index i
        if bitstream[i:i + 8] == "00000000":
            p = last_polarity
            # Substitution voltages: 0, 0, 0, V, B, 0, V, B
            sub_voltages = [0, 0, 0, p, -p, 0, -p, p]
            
            p_sign = "+" if p > 0 else "-"
            inv_sign = "-" if p > 0 else "+"
            sub_symbols = ["0", "0", "0", f"V{p_sign}", f"B{inv_sign}", "0", f"V{inv_sign}", f"B{p_sign}"]
            
            levels.extend(sub_voltages)
            symbols.extend(sub_symbols)
            
            # The last pulse in 000VB0VB has polarity p
            last_polarity = p
            i += 8
        else:
            bit = bitstream[i]
            if bit == '0':
                levels.append(0)
                symbols.append("0")
            else:
                last_polarity = -last_polarity
                levels.append(last_polarity)
                symbols.append("+" if last_polarity > 0 else "-")
            i += 1
            
    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    
    return levels, symbols, time, voltage


def scramble_hdb3(bitstream: str, initial_polarity: int = -1):
    """
    HDB3 (High-Density Bipolar 3-Zero):
    Replaces any run of 4 consecutive zeros ('0000') based on:
    - Pulse count (number of non-zero pulses since last substitution):
      * If Odd  -> substitute '000V' (V has same polarity as last pulse)
      * If Even -> substitute 'B00V' (B has opposite polarity to last pulse, V has same polarity as B)
      
    Returns:
        tuple: (levels, symbols, time, voltage)
    """
    levels = []
    symbols = []
    last_polarity = initial_polarity
    pulse_count_since_sub = 0
    
    i = 0
    n = len(bitstream)
    
    while i < n:
        if bitstream[i:i + 4] == "0000":
            p = last_polarity
            if pulse_count_since_sub % 2 == 1:
                # Odd pulse count: 000V
                v_polarity = p
                sub_voltages = [0, 0, 0, v_polarity]
                v_sign = "+" if v_polarity > 0 else "-"
                sub_symbols = ["0", "0", "0", f"V{v_sign}"]
                last_polarity = v_polarity
            else:
                # Even pulse count: B00V
                b_polarity = -p
                v_polarity = b_polarity
                sub_voltages = [b_polarity, 0, 0, v_polarity]
                b_sign = "+" if b_polarity > 0 else "-"
                v_sign = "+" if v_polarity > 0 else "-"
                sub_symbols = [f"B{b_sign}", "0", "0", f"V{v_sign}"]
                last_polarity = v_polarity
                
            levels.extend(sub_voltages)
            symbols.extend(sub_symbols)
            pulse_count_since_sub = 0  # Reset pulse counter after substitution
            i += 4
        else:
            bit = bitstream[i]
            if bit == '0':
                levels.append(0)
                symbols.append("0")
            else:
                last_polarity = -last_polarity
                levels.append(last_polarity)
                symbols.append("+" if last_polarity > 0 else "-")
                pulse_count_since_sub += 1
            i += 1
            
    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    
    return levels, symbols, time, voltage


def scramble_signal(bitstream: str, scheme: str = "B8ZS"):
    """
    Unified function to apply scrambling to an AMI signal.
    Supported schemes: 'B8ZS', 'HDB3'
    """
    normalized = scheme.strip().upper()
    if normalized == "B8ZS":
        return scramble_b8zs(bitstream)
    elif normalized == "HDB3":
        return scramble_hdb3(bitstream)
    else:
        raise ValueError(f"Unknown scrambling scheme: {scheme}. Choose 'B8ZS' or 'HDB3'.")


# ^^^^^^^^ Test ke liye likha hai maine (START) ^^^^^^^^
# (Yeh section sirf is file ko akele chala kar check karne ke liye hai, main project logic upar hai)
if __name__ == "__main__":
    from data_generator import generate_bits_with_zero_runs
    from plotter import plot_line_code

    print("--- AMI Scrambling Schemes Test (B8ZS & HDB3) ---")

    # 1. Test Longest Zero Run (Competitive coding O(N))
    test_stream = "1100001000000001"
    zero_run = find_longest_zero_run(test_stream)
    print("\n[Competitive Coding - Longest Zero Run]")
    print("Stream        :", test_stream)
    print("Longest 0 Run : Length =", zero_run["length"], 
          f"from index {zero_run['start_index']} to {zero_run['end_index']}")

    # 2. Test B8ZS with 8-zero pattern
    b8zs_input = "110000000010"
    b8zs_levels, b8zs_syms, t1, v1 = scramble_b8zs(b8zs_input)
    print("\n[B8ZS Test]")
    print("Input Bits    :", b8zs_input)
    print("Scrambled Syms:", " ".join(b8zs_syms))
    print("Voltage Levels:", b8zs_levels)
    plot_line_code(b8zs_input, t1, v1, "AMI with B8ZS Scrambling", 
                   labels=b8zs_syms, save_path="b8zs_test.png")

    # 3. Test HDB3 with multiple 4-zero patterns (testing both Odd and Even cases)
    hdb3_input = "10000110000"
    hdb3_levels, hdb3_syms, t2, v2 = scramble_hdb3(hdb3_input)
    print("\n[HDB3 Test]")
    print("Input Bits    :", hdb3_input)
    print("Scrambled Syms:", " ".join(hdb3_syms))
    print("Voltage Levels:", hdb3_levels)
    plot_line_code(hdb3_input, t2, v2, "AMI with HDB3 Scrambling", 
                   labels=hdb3_syms, save_path="hdb3_test.png")

    print("\nScrambling tests completed successfully.")
# ^^^^^^^^ Test ke liye likha hai maine (END) ^^^^^^^^
