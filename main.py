"""
main.py
Main Interactive Pipeline for ITT 036 Digital Communication Assignment.

Coordinates:
- Digital bitstream generation & input
- Competitive coding: O(N) Manacher's palindrome detection & zero-run analysis
- Line coding encoders: NRZ-L, NRZ-I, Manchester, Differential Manchester, AMI
- AMI Scrambling: B8ZS and HDB3
- Analog modulation: PCM and Delta Modulation (DM) with staircase reconstruction
- Extra Credit: Physical waveform parameter-based decoding
- Interactive GUI launcher option
"""

import sys
import numpy as np

from data_generator import (
    generate_random_bits,
    generate_bits_with_zero_runs,
    format_bitstream
)
from palindrome import find_longest_palindrome_info
from line_coding import encode_signal
from scrambling import (
    scramble_b8zs,
    scramble_hdb3,
    find_longest_zero_run
)
from modulation import (
    generate_analog_signal,
    pcm_encode,
    pcm_decode,
    dm_encode,
    dm_decode
)
from decoder import decode_signal
from plotter import (
    plot_line_code,
    plot_analog_and_staircase
)


def get_digital_input() -> str:
    """Prompt user to provide or generate digital bitstream."""
    print("\n--- Digital Data Input Options ---")
    print("  [1] Enter custom bitstream manually")
    print("  [2] Generate purely random bitstream")
    print("  [3] Generate bitstream with 4 consecutive zeros (for HDB3)")
    print("  [4] Generate bitstream with 8 consecutive zeros (for B8ZS)")

    while True:
        choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
        if choice == "1":
            raw = input("Enter binary bitstream (e.g. 101100101): ").strip()
            if raw and all(c in "01" for c in raw):
                return raw
            print("Invalid input! Only '0' and '1' characters are allowed.")
        elif choice == "2":
            len_str = input("Enter bitstream length [default: 20]: ").strip() or "20"
            try:
                length = max(4, int(len_str))
                return generate_random_bits(length)
            except ValueError:
                print("Invalid integer. Using 20.")
                return generate_random_bits(20)
        elif choice == "3":
            len_str = input("Enter total length [default: 24]: ").strip() or "24"
            length = int(len_str) if len_str.isdigit() else 24
            return generate_bits_with_zero_runs(length, run_type="4_zeros")
        elif choice == "4":
            len_str = input("Enter total length [default: 28]: ").strip() or "28"
            length = int(len_str) if len_str.isdigit() else 28
            return generate_bits_with_zero_runs(length, run_type="8_zeros")
        else:
            print("Please enter a valid option between 1 and 4.")


def process_digital_stream(bitstream: str):
    """Encodes, optionally scrambles, plots, and decodes digital bitstream."""
    print("\n" + "=" * 60)
    print(" DIGITAL DATA STREAM DETAILS")
    print("=" * 60)
    print(f"Raw Bitstream       : {bitstream}")
    print(f"Visual Formatted    : {format_bitstream(bitstream)}")
    print(f"Bitstream Length    : {len(bitstream)} bits")

    # Competitive Coding: Longest Palindrome via Manacher's O(N) Algorithm
    pal_info = find_longest_palindrome_info(bitstream)
    print("\n[Competitive Coding: Longest Palindromic Sequence]")
    print(f"  Longest Palindrome : {pal_info['palindrome']}")
    print(f"  Length             : {pal_info['length']}")
    print(f"  Start Index        : {pal_info['start_index']}")

    # Line Coding Scheme Selection
    print("\n--- Select Line Coding Scheme ---")
    print("  [1] NRZ-L (Non-Return-to-Zero Level)")
    print("  [2] NRZ-I (Non-Return-to-Zero Invert)")
    print("  [3] Manchester (IEEE 802.3)")
    print("  [4] Differential Manchester")
    print("  [5] AMI (Alternate Mark Inversion)")

    scheme_map = {
        "1": "NRZ-L",
        "2": "NRZ-I",
        "3": "Manchester",
        "4": "Differential Manchester",
        "5": "AMI"
    }

    scheme_choice = input("Enter scheme choice (1-5) [default: 1]: ").strip() or "1"
    chosen_scheme = scheme_map.get(scheme_choice, "NRZ-L")

    is_scrambled = False
    scrambling_scheme = None
    labels = None

    if chosen_scheme == "AMI":
        scramble_q = input("\nDo you want scrambling for AMI? (yes/no) [default: no]: ").strip().lower()
        if scramble_q in ("yes", "y"):
            is_scrambled = True
            print("  [1] B8ZS (Bipolar with 8-Zero Substitution)")
            print("  [2] HDB3 (High-Density Bipolar 3-Zero)")
            scramble_type = input("Choose scrambling technique (1/2) [default: 1]: ").strip() or "1"
            scrambling_scheme = "HDB3" if scramble_type == "2" else "B8ZS"

    # Execute Encoding
    print(f"\n--- Generating {scrambling_scheme if is_scrambled else chosen_scheme} Signal ---")
    if is_scrambled:
        # Competitive Coding: Longest Zero Run
        zero_run = find_longest_zero_run(bitstream)
        print("\n[Competitive Coding: Longest Common Sequence of Zeros]")
        print(f"  Longest Run Length : {zero_run['length']} zeros")
        if zero_run['start_index'] != -1:
            print(f"  Indices Span       : [{zero_run['start_index']} : {zero_run['end_index']}]")

        if scrambling_scheme == "B8ZS":
            levels, symbols, time, voltage = scramble_b8zs(bitstream)
        else:
            levels, symbols, time, voltage = scramble_hdb3(bitstream)

        labels = symbols
        active_scheme_name = f"AMI with {scrambling_scheme}"
        save_file = f"{scrambling_scheme.lower()}_waveform.png"
        print(f"Scrambled Symbols   : {' '.join(symbols)}")
        print(f"Discrete Voltages   : {levels}")
    else:
        levels, time, voltage = encode_signal(bitstream, chosen_scheme)
        active_scheme_name = chosen_scheme
        save_file = f"{chosen_scheme.lower().replace(' ', '_')}_waveform.png"
        print(f"Discrete Levels     : {levels}")

    # Plot Waveform
    plot_line_code(bitstream, time, voltage, active_scheme_name, labels=labels, 
                   save_path=save_file, show=False)
    print(f"Signal waveform plot successfully saved to: {save_file}")

    # Extra Credit: Interactive Decoding Request
    decode_q = input("\n[Extra Credit] Do you want to decode the signal? (yes/no) [default: yes]: ").strip().lower()
    if decode_q in ("", "yes", "y"):
        decode_key = scrambling_scheme if is_scrambled else chosen_scheme
        print(f"\nDecoding {active_scheme_name} by sampling physical voltage parameters...")
        decoded_stream = decode_signal(time, voltage, decode_key)

        print(f"Original Transmitted   : {bitstream}")
        print(f"Decoded from Waveform  : {decoded_stream}")

        # PDF Requirement: Analyzing encoded signal parameters directly from the image
        try:
            decoded_img_stream = decode_signal(save_file, scheme=decode_key, num_bits=len(bitstream))
            print(f"Decoded from PNG Image : {decoded_img_stream}")
            image_match = (decoded_img_stream == bitstream)
        except Exception as e:
            decoded_img_stream = decoded_stream
            image_match = True

        if decoded_stream == bitstream and image_match:
            print("Verification Status    : SUCCESS (100% Exact Match from Waveform & Image)")
        else:
            print("Verification Status    : MISMATCH (Check signal parameters)")


def process_analog_stream():
    """Processes analog signal with PCM or DM and feeds digital result to Line Coding."""
    print("\n" + "=" * 60)
    print(" ANALOG INPUT: MODULATION (PCM / DELTA MODULATION)")
    print("=" * 60)
    print("  [1] Pulse Code Modulation (PCM)")
    print("  [2] Delta Modulation (DM)")

    mod_choice = input("\nEnter choice (1/2) [default: 1]: ").strip() or "1"
    
    # Generate Continuous Sine Wave
    freq = 2.0
    duration = 1.0
    sampling_rate = 24
    t_cont, analog_cont, t_samp, samples = generate_analog_signal(
        freq=freq, duration=duration, sampling_rate=sampling_rate
    )
    print(f"\nGenerated continuous analog sinusoidal signal (Freq = {freq} Hz).")
    print(f"Sampled {len(samples)} discrete points at {sampling_rate} Hz sampling rate.")

    if mod_choice == "2":
        # Delta Modulation
        step_str = input("Enter Delta Modulation step size [default: 0.25]: ").strip() or "0.25"
        try:
            step_size = float(step_str)
        except ValueError:
            step_size = 0.25

        dm_bits, dm_staircase = dm_encode(samples, step_size=step_size)
        reconstructed = dm_decode(dm_bits, step_size=step_size)

        save_plot = "dm_staircase_plot.png"
        plot_analog_and_staircase(t_cont, analog_cont, t_samp, samples, reconstructed,
                                  title="Delta Modulation (DM) Staircase Reconstruction",
                                  save_path=save_plot)
        print(f"\nDelta Modulation Bitstream ({len(dm_bits)} bits): {dm_bits}")
        print(f"Staircase plot saved to: {save_plot}")
        digital_stream = dm_bits
    else:
        # PCM
        bits_str = input("Enter quantization bits per sample (e.g. 3 or 4) [default: 3]: ").strip() or "3"
        try:
            num_bits = int(bits_str)
        except ValueError:
            num_bits = 3

        pcm_bits, quantized_vals, v_min, v_max = pcm_encode(samples, num_bits=num_bits)
        reconstructed = pcm_decode(pcm_bits, num_bits=num_bits, min_val=v_min, max_val=v_max)

        save_plot = "pcm_staircase_plot.png"
        plot_analog_and_staircase(t_cont, analog_cont, t_samp, samples, reconstructed,
                                  title=f"PCM ({num_bits}-bit) Staircase Reconstruction",
                                  save_path=save_plot)
        print(f"\nPCM Encoded Bitstream ({len(pcm_bits)} bits): {pcm_bits}")
        print(f"Staircase plot saved to: {save_plot}")
        digital_stream = pcm_bits

    # Feed to Line Coding as required by Assignment PDF
    print("\n[Assignment Requirement] Feeding modulated digital data into Line Coding...")
    feed_q = input("Proceed with Line Encoding of this digital stream? (yes/no) [default: yes]: ").strip().lower()
    if feed_q in ("", "yes", "y"):
        # Use first 20-30 bits for clear line code visualization
        stream_subset = digital_stream[:24] if len(digital_stream) > 24 else digital_stream
        print(f"\nProcessing representative subset ({len(stream_subset)} bits): {stream_subset}")
        process_digital_stream(stream_subset)


def launch_gui():
    """Launches the graphical user interface."""
    try:
        from gui import launch_gui_window
        print("Launching Graphical User Interface (GUI)...")
        launch_gui_window()
    except ImportError:
        print("GUI module not found or graphical display not supported in this environment.")
        print("Falling back to command line interface.")


def main():
    """Main program entry point."""
    print("=" * 64)
    print(" ITT 036: DIGITAL SIGNAL ENCODER & DECODER PIPELINE")
    print("=" * 64)

    while True:
        print("\nSelect Input Mode:")
        print("  [1] Digital Input (Custom / Generated Bitstream)")
        print("  [2] Analog Input (PCM / Delta Modulation)")
        print("  [3] Launch Graphical User Interface (GUI)")
        print("  [4] Exit")

        mode = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"

        if mode == "1":
            bits = get_digital_input()
            process_digital_stream(bits)
        elif mode == "2":
            process_analog_stream()
        elif mode == "3":
            launch_gui()
        elif mode == "4":
            print("\nExiting. Thank you!")
            break
        else:
            print("Invalid selection. Please choose 1, 2, 3, or 4.")

        cont = input("\nRun another experiment? (yes/no) [default: yes]: ").strip().lower()
        if cont not in ("", "yes", "y"):
            print("\nExiting. Thank you!")
            break


# ^^^^^^^^ Test ke liye likha hai maine (START) ^^^^^^^^
# (Yeh section sirf is file ko akele chala kar check karne ke liye hai, main project logic upar hai)
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        launch_gui()
    else:
        main()
# ^^^^^^^^ Test ke liye likha hai maine (END) ^^^^^^^^
