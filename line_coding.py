"""
line_coding.py
Implements digital line coding schemes:
- NRZ-L (Non-Return-to-Zero Level)
- NRZ-I (Non-Return-to-Zero Invert)
- Manchester (IEEE 802.3)
- Differential Manchester
- AMI (Alternate Mark Inversion)
"""

import numpy as np


def encode_nrz_l(bitstream: str):
    """
    NRZ-L (Non-Return-to-Zero Level):
    - Bit '0': High voltage (+1V)
    - Bit '1': Low voltage (-1V)
    """
    levels = [1 if bit == '0' else -1 for bit in bitstream]
    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    return levels, time, voltage


def encode_nrz_i(bitstream: str, initial_level: int = 1):
    """
    NRZ-I (Non-Return-to-Zero Invert):
    - Bit '0': No transition (level remains same as previous bit)
    - Bit '1': Transition occurs at beginning of bit (invert level)
    """
    levels = []
    curr = initial_level
    for bit in bitstream:
        if bit == '1':
            curr = -curr
        levels.append(curr)

    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    return levels, time, voltage


def encode_manchester(bitstream: str):
    """
    Manchester (IEEE 802.3 convention):
    - Transition in the middle of each bit interval.
    - Bit '0': High (+1V) to Low (-1V) transition.
    - Bit '1': Low (-1V) to High (+1V) transition.
    """
    levels = []
    samples_per_bit = 100
    half_samples = samples_per_bit // 2
    voltage_segments = []

    for bit in bitstream:
        if bit == '0':
            first_half, second_half = 1, -1
        else:
            first_half, second_half = -1, 1

        levels.extend([first_half, second_half])
        voltage_segments.append(np.full(half_samples, first_half))
        voltage_segments.append(np.full(half_samples, second_half))

    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.concatenate(voltage_segments)
    return levels, time, voltage


def encode_diff_manchester(bitstream: str, initial_level: int = 1):
    """
    Differential Manchester:
    - Mid-bit transition always occurs for clock synchronization.
    - Bit '0': Transition at beginning of bit interval.
    - Bit '1': No transition at beginning of bit interval.
    """
    levels = []
    curr = initial_level
    samples_per_bit = 100
    half_samples = samples_per_bit // 2
    voltage_segments = []

    for bit in bitstream:
        if bit == '0':
            # Transition at beginning
            first_half = -curr
            second_half = curr
        else:
            # No transition at beginning
            first_half = curr
            second_half = -curr

        curr = second_half
        levels.extend([first_half, second_half])
        voltage_segments.append(np.full(half_samples, first_half))
        voltage_segments.append(np.full(half_samples, second_half))

    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.concatenate(voltage_segments)
    return levels, time, voltage


def encode_ami(bitstream: str, initial_polarity: int = -1):
    """
    AMI (Alternate Mark Inversion):
    - Bit '0': Zero voltage (0V)
    - Bit '1': Alternating positive (+1V) and negative (-1V) voltages.
    """
    levels = []
    last_one_polarity = initial_polarity

    for bit in bitstream:
        if bit == '0':
            levels.append(0)
        else:
            last_one_polarity = -last_one_polarity
            levels.append(last_one_polarity)

    samples_per_bit = 100
    time = np.linspace(0, len(bitstream), len(bitstream) * samples_per_bit)
    voltage = np.repeat(levels, samples_per_bit)
    return levels, time, voltage


def encode_signal(bitstream: str, scheme: str):
    """
    Unified dispatcher to encode bitstream using the requested scheme name.
    Supported schemes: 'NRZ-L', 'NRZ-I', 'Manchester', 'Differential Manchester', 'AMI'
    """
    normalized = scheme.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    if normalized == "nrzl":
        return encode_nrz_l(bitstream)
    elif normalized == "nrzi":
        return encode_nrz_i(bitstream)
    elif normalized == "manchester":
        return encode_manchester(bitstream)
    elif normalized in ("differentialmanchester", "diffmanchester"):
        return encode_diff_manchester(bitstream)
    elif normalized == "ami":
        return encode_ami(bitstream)
    else:
        raise ValueError(f"Unknown line coding scheme: {scheme}")


if __name__ == "__main__":
    from plotter import plot_line_code

    test_stream = "1011001"
    print("--- Testing All 5 Line Coding Encoders ---")
    print("Input Bitstream:", test_stream)

    schemes = [
        "NRZ-L",
        "NRZ-I",
        "Manchester",
        "Differential Manchester",
        "AMI"
    ]

    for name in schemes:
        levels, t, v = encode_signal(test_stream, name)
        print(f"\n[{name}]")
        print("Discrete Levels:", levels)
        plot_line_code(test_stream, t, v, name, save_path=f"{name.lower().replace(' ', '_')}_test.png")

    print("\nAll 5 line coding checks completed successfully.")

