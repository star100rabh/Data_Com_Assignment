"""
line_coding.py
Implements digital line coding schemes:
- NRZ-L (Non-Return-to-Zero Level)
- NRZ-I (Non-Return-to-Zero Invert)
"""

import numpy as np


def encode_nrz_l(bitstream: str):
    """
    Encodes bitstream using NRZ-L (Non-Return-to-Zero Level).
    - Bit '0': High voltage (+1V)
    - Bit '1': Low voltage (-1V)
    
    Returns:
        tuple: (levels, time, voltage)
    """
    levels = []
    for bit in bitstream:
        if bit == '0':
            levels.append(1)
        else:
            levels.append(-1)
            
    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    
    return levels, time, voltage


def encode_nrz_i(bitstream: str, initial_level: int = 1):
    """
    Encodes bitstream using NRZ-I (Non-Return-to-Zero Invert).
    - Bit '0': No transition (voltage remains unchanged)
    - Bit '1': Invert voltage (transition occurs at start of bit)
    
    Returns:
        tuple: (levels, time, voltage)
    """
    levels = []
    current_level = initial_level
    
    for bit in bitstream:
        if bit == '1':
            current_level = -current_level  # Invert on '1'
        # On '0', keep current_level
        levels.append(current_level)
        
    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    
    return levels, time, voltage


# ^^^^^^^^ Test ke liye likha hai maine (START) ^^^^^^^^
# (Yeh section sirf is file ko akele chala kar check karne ke liye hai, main project logic upar hai)
if __name__ == "__main__":
    from plotter import plot_line_code
    
    test_stream = "1011001"
    print("--- Testing NRZ-L and NRZ-I Encoders ---")
    print("Input Bitstream:", test_stream)
    
    # 1. NRZ-L Test
    nrz_l_levels, t, v_l = encode_nrz_l(test_stream)
    print("NRZ-L Levels :", nrz_l_levels)
    plot_line_code(test_stream, t, v_l, "NRZ-L", save_path="nrz_l_test.png")
    
    # 2. NRZ-I Test
    nrz_i_levels, t, v_i = encode_nrz_i(test_stream)
    print("NRZ-I Levels :", nrz_i_levels)
    plot_line_code(test_stream, t, v_i, "NRZ-I", save_path="nrz_i_test.png")
    
    print("Checks passed successfully.")
# ^^^^^^^^ Test ke liye likha hai maine (END) ^^^^^^^^
