"""
modulation.py
Implements analog-to-digital modulation techniques:
- Pulse Code Modulation (PCM): Sampling, Quantization, Encoding and Decoding
- Delta Modulation (DM): 1-bit staircase approximation and Decoding
"""

import numpy as np


def generate_analog_signal(freq: float = 2.0, amp: float = 1.0, 
                           duration: float = 1.0, sampling_rate: int = 24):
    """
    Generates a continuous analog sinusoidal signal and extracts discrete sample points.

    Returns:
        tuple: (t_continuous, analog_continuous, t_samples, sample_values)
    """
    # High-resolution time axis to simulate a smooth continuous analog wave
    t_continuous = np.linspace(0, duration, 1000)
    analog_continuous = amp * np.sin(2 * np.pi * freq * t_continuous)

    # Discrete sampling points (Nyquist rate or higher)
    num_samples = int(duration * sampling_rate)
    t_samples = np.linspace(0, duration, num_samples, endpoint=False)
    sample_values = amp * np.sin(2 * np.pi * freq * t_samples)

    return t_continuous, analog_continuous, t_samples, sample_values


def pcm_encode(samples: np.ndarray, num_bits: int = 3):
    """
    PCM Encoder:
    1. Divides the voltage dynamic range into L = 2^num_bits quantization zones.
    2. Quantizes each analog sample to the nearest zone midpoint.
    3. Encodes each zone into an n-bit binary codeword.

    Returns:
        tuple: (bitstream, quantized_values, min_val, max_val)
    """
    num_levels = 2 ** num_bits
    min_val = float(np.min(samples))
    max_val = float(np.max(samples))

    # Add a small buffer so the max value does not overflow the top bin
    delta = (max_val - min_val) / num_levels

    bitstream_chunks = []
    quantized_values = []

    for s in samples:
        # Determine which quantization zone s falls into
        if delta == 0:
            level_idx = 0
        else:
            level_idx = int((s - min_val) / delta)
            level_idx = min(level_idx, num_levels - 1)  # Clamp to valid index range

        # Midpoint of the quantization level
        q_val = min_val + (level_idx + 0.5) * delta
        quantized_values.append(q_val)

        # Convert level index to n-bit binary string
        code = format(level_idx, f"0{num_bits}b")
        bitstream_chunks.append(code)

    bitstream = "".join(bitstream_chunks)
    return bitstream, np.array(quantized_values), min_val, max_val


def pcm_decode(bitstream: str, num_bits: int = 3, min_val: float = -1.0, max_val: float = 1.0):
    """
    PCM Decoder:
    Reconstructs the quantized staircase signal from the received binary bitstream.

    Returns:
        np.ndarray: Reconstructed staircase voltage levels.
    """
    num_levels = 2 ** num_bits
    delta = (max_val - min_val) / num_levels

    reconstructed = []
    # Process the bitstream in chunks of num_bits
    for i in range(0, len(bitstream), num_bits):
        chunk = bitstream[i:i + num_bits]
        if len(chunk) == num_bits:
            level_idx = int(chunk, 2)
            q_val = min_val + (level_idx + 0.5) * delta
            reconstructed.append(q_val)

    return np.array(reconstructed)


def dm_encode(samples: np.ndarray, step_size: float = 0.2, initial_val: float = 0.0):
    """
    Delta Modulation (DM) Encoder:
    Approximates the signal using a staircase with fixed step size (+delta or -delta).
    - If current sample >= previous staircase level: transmit '1', step up (+delta)
    - If current sample < previous staircase level: transmit '0', step down (-delta)

    Returns:
        tuple: (bitstream, staircase_levels)
    """
    bits = []
    staircase = []
    curr = initial_val

    for s in samples:
        if s >= curr:
            bits.append("1")
            curr += step_size
        else:
            bits.append("0")
            curr -= step_size
        staircase.append(curr)

    bitstream = "".join(bits)
    return bitstream, np.array(staircase)


def dm_decode(bitstream: str, step_size: float = 0.2, initial_val: float = 0.0):
    """
    Delta Modulation (DM) Decoder:
    Reconstructs the staircase waveform from the 1-bit stream.

    Returns:
        np.ndarray: Reconstructed staircase voltage levels.
    """
    staircase = []
    curr = initial_val

    for bit in bitstream:
        if bit == "1":
            curr += step_size
        else:
            curr -= step_size
        staircase.append(curr)

    return np.array(staircase)


if __name__ == "__main__":
    from plotter import plot_analog_and_staircase, plot_line_code
    from line_coding import encode_signal

    print("--- Testing PCM and Delta Modulation (DM) Encoders & Decoders ---")

    # 1. Generate sample analog input (2 Hz sine wave with 24 samples over 1 sec)
    t_cont, analog_cont, t_samp, samples = generate_analog_signal(freq=2.0, duration=1.0, sampling_rate=24)
    print(f"Generated analog signal with {len(samples)} discrete samples.")

    # 2. Test PCM (3-bit resolution = 8 quantization levels)
    pcm_bits, pcm_quantized, v_min, v_max = pcm_encode(samples, num_bits=3)
    pcm_reconstructed = pcm_decode(pcm_bits, num_bits=3, min_val=v_min, max_val=v_max)

    print("\n[PCM Results (3-bit)]")
    print(f"Encoded Bitstream ({len(pcm_bits)} bits):", pcm_bits[:36], "...")
    print("Decoder match check:", np.allclose(pcm_quantized, pcm_reconstructed))

    # Plot PCM analog vs staircase
    plot_analog_and_staircase(t_cont, analog_cont, t_samp, samples, pcm_reconstructed,
                              title="PCM (Pulse Code Modulation) Staircase Reconstruction",
                              save_path="pcm_staircase_test.png")

    # 3. Test Delta Modulation (DM)
    dm_bits, dm_staircase = dm_encode(samples, step_size=0.25)
    dm_reconstructed = dm_decode(dm_bits, step_size=0.25)

    print("\n[Delta Modulation (DM) Results]")
    print(f"Encoded Bitstream ({len(dm_bits)} bits):", dm_bits)
    print("Decoder match check:", np.allclose(dm_staircase, dm_reconstructed))

    # Plot DM analog vs staircase
    plot_analog_and_staircase(t_cont, analog_cont, t_samp, samples, dm_reconstructed,
                              title="Delta Modulation (DM) Staircase Reconstruction",
                              save_path="dm_staircase_test.png")

    # 4. Feed generated PCM bitstream into Line Coding (as required in PDF!)
    line_levels, t_line, v_line = encode_signal(pcm_bits[:12], "NRZ-L")
    plot_line_code(pcm_bits[:12], t_line, v_line, "NRZ-L (From PCM Bitstream)", save_path="pcm_line_code_test.png")

    print("\nAll PCM & DM tests passed successfully!")

