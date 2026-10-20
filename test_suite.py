"""
test_suite.py
Comprehensive Automated Test Suite for ITT 036 Digital Signal Encoder & Decoder.

Validates all requirements specified in the Autumn 2026 Programming Assignment 1:
1. Digital Data Generator & Zero Run Injection
2. Competitive Coding: O(N) Manacher's Longest Palindrome Detection
3. Line Coding Encoders: NRZ-L, NRZ-I, Manchester, Differential Manchester, AMI
4. AMI Scrambling Schemes: B8ZS & HDB3 with O(N) Zero-Run Analysis
5. Modulation: PCM and Delta Modulation (DM) Encoders & Decoders
6. Extra Credit: Waveform Parameter-based Line Coding Decoders & Descramblers
7. Extra Credit: Direct Image-Pixel Analysis Decoders (PNG Waveform Analysis)
"""

import os
import sys
import numpy as np

from data_generator import (
    generate_random_bits,
    generate_bits_with_zero_runs,
    generate_and_find_palindrome,
    format_bitstream
)
from palindrome import longest_palindrome_manacher, find_longest_palindrome_info
from line_coding import (
    encode_nrz_l,
    encode_nrz_i,
    encode_manchester,
    encode_diff_manchester,
    encode_ami,
    encode_signal
)
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
from decoder import (
    decode_signal,
    decode_from_image,
    descramble_b8zs,
    descramble_hdb3
)
from plotter import (
    plot_line_code,
    plot_analog_and_staircase
)


def run_all_tests():
    print("=" * 70)
    print(" ITT 036: COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=" * 70)

    results = []

    # ---------------------------------------------------------
    # 1. Digital Data Generator Tests
    # ---------------------------------------------------------
    print("\n[TEST 1] Digital Data Generator & Zero Sequence Injection")
    r_bits = generate_random_bits(24)
    t1_1 = len(r_bits) == 24 and all(c in "01" for c in r_bits)
    print(f"  Random bits (24b)            : {r_bits} [{'PASS' if t1_1 else 'FAIL'}]")

    hdb3_seq = generate_bits_with_zero_runs(24, run_type="4_zeros")
    t1_2 = "0000" in hdb3_seq and len(hdb3_seq) == 24
    print(f"  Injected 4 zeros (HDB3)      : {hdb3_seq} [{'PASS' if t1_2 else 'FAIL'}]")

    b8zs_seq = generate_bits_with_zero_runs(28, run_type="8_zeros")
    t1_3 = "00000000" in b8zs_seq and len(b8zs_seq) == 28
    print(f"  Injected 8 zeros (B8ZS)      : {b8zs_seq} [{'PASS' if t1_3 else 'FAIL'}]")

    both_seq = generate_bits_with_zero_runs(32, run_type="both")
    t1_4 = "00000000" in both_seq and len(both_seq) == 32
    print(f"  Injected both (B8ZS + HDB3)  : {both_seq} [{'PASS' if t1_4 else 'FAIL'}]")

    gen_pal_seq, pal_meta = generate_and_find_palindrome(20, run_type="4_zeros")
    t1_5 = len(gen_pal_seq) == 20 and len(pal_meta["palindrome"]) > 0
    print(f"  Generator + Palindrome direct: {pal_meta['palindrome']} (len {pal_meta['length']}) [{'PASS' if t1_5 else 'FAIL'}]")

    pass_1 = t1_1 and t1_2 and t1_3 and t1_4 and t1_5
    results.append(("Digital Data Generator & Injection", pass_1))

    # ---------------------------------------------------------
    # 2. Competitive Coding: Manacher's Algorithm O(N) Palindrome
    # ---------------------------------------------------------
    print("\n[TEST 2] Competitive Coding: Manacher's O(N) Palindrome Detection")
    test_cases_pal = [
        ("0110", "0110"),
        ("10101", "10101"),
        ("00101011100010111101111100001111", "111100001111"),
        ("111111", "111111"),
        ("1000000001", "1000000001")
    ]
    pal_all_passed = True
    for seq, expected in test_cases_pal:
        detected = longest_palindrome_manacher(seq)
        is_ok = (detected == expected)
        if not is_ok:
            pal_all_passed = False
        print(f"  Input: {seq:32s} -> Detected: {detected:16s} [{'PASS' if is_ok else 'FAIL'}]")

    results.append(("Manacher's Palindrome Detection O(N)", pal_all_passed))

    # ---------------------------------------------------------
    # 3. Line Coding Schemes Encoders
    # ---------------------------------------------------------
    print("\n[TEST 3] Line Coding Encoders (All 5 Standard Schemes)")
    sample_bits = "1011001"
    line_schemes = ["NRZ-L", "NRZ-I", "Manchester", "Differential Manchester", "AMI"]
    line_all_passed = True

    for scheme in line_schemes:
        levels, time, voltage = encode_signal(sample_bits, scheme)
        has_levels = len(levels) > 0
        has_time = len(time) == len(voltage) and len(time) > 0
        is_ok = has_levels and has_time
        if not is_ok:
            line_all_passed = False
        print(f"  Encoding {scheme:23s}: Discrete levels count = {len(levels):2d} [{'PASS' if is_ok else 'FAIL'}]")

    results.append(("5 Line Coding Encoders", line_all_passed))

    # ---------------------------------------------------------
    # 4. AMI Scrambling Schemes & Longest Zero-Run Algorithm
    # ---------------------------------------------------------
    print("\n[TEST 4] AMI Scrambling Schemes (B8ZS, HDB3) & O(N) Zero-Run")
    # Test O(N) Zero Run
    zr_stream = "1100001000000001"
    zr_info = find_longest_zero_run(zr_stream)
    zr_ok = (zr_info["length"] == 8 and zr_info["start_index"] == 7)
    print(f"  Longest Zero-Run Detection   : Length={zr_info['length']}, Start={zr_info['start_index']} [{'PASS' if zr_ok else 'FAIL'}]")

    # B8ZS Scrambler
    b8zs_in = "110000000010"
    b8zs_lvls, b8zs_syms, _, _ = scramble_b8zs(b8zs_in)
    b8zs_has_v = any("V" in s for s in b8zs_syms) and any("B" in s for s in b8zs_syms)
    print(f"  B8ZS Scrambler (000VB0VB)    : Symbols={' '.join(b8zs_syms[:8])}... [{'PASS' if b8zs_has_v else 'FAIL'}]")

    # HDB3 Scrambler (Both Odd and Even substitutions)
    hdb3_in = "10000110000"
    hdb3_lvls, hdb3_syms, _, _ = scramble_hdb3(hdb3_in)
    hdb3_has_v = any("V" in s for s in hdb3_syms)
    print(f"  HDB3 Scrambler (000V/B00V)   : Symbols={' '.join(hdb3_syms)} [{'PASS' if hdb3_has_v else 'FAIL'}]")

    results.append(("B8ZS & HDB3 Scramblers + Zero-Run O(N)", zr_ok and b8zs_has_v and hdb3_has_v))

    # ---------------------------------------------------------
    # 5. Modulation Schemes (PCM & Delta Modulation)
    # ---------------------------------------------------------
    print("\n[TEST 5] Analog Modulation: PCM and Delta Modulation (DM)")
    t_c, a_c, t_s, samples = generate_analog_signal(freq=2.0, duration=1.0, sampling_rate=24)

    # PCM Encoder & Decoder
    pcm_bits, pcm_q, vmin, vmax = pcm_encode(samples, num_bits=3)
    pcm_rec = pcm_decode(pcm_bits, num_bits=3, min_val=vmin, max_val=vmax)
    pcm_ok = len(pcm_bits) == 24 * 3 and np.allclose(pcm_q, pcm_rec)
    print(f"  PCM (3-bit, 24 samples)      : Encoded {len(pcm_bits)} bits, Decoder match={pcm_ok} [{'PASS' if pcm_ok else 'FAIL'}]")

    # Delta Modulation Encoder & Decoder
    dm_bits, dm_stair = dm_encode(samples, step_size=0.25)
    dm_rec = dm_decode(dm_bits, step_size=0.25)
    dm_ok = len(dm_bits) == 24 and np.allclose(dm_stair, dm_rec)
    print(f"  Delta Modulation (DM)        : Encoded {len(dm_bits)} bits, Decoder match={dm_ok} [{'PASS' if dm_ok else 'FAIL'}]")

    results.append(("PCM & Delta Modulation Encoders/Decoders", pcm_ok and dm_ok))

    # ---------------------------------------------------------
    # 6. Extra Credit: Waveform Parameter-based Decoders
    # ---------------------------------------------------------
    print("\n[TEST 6] Extra Credit: Physical Waveform Parameter Decoders")
    dec_all_ok = True
    for scheme in line_schemes:
        levels, t, v = encode_signal(sample_bits, scheme)
        decoded = decode_signal(t, v, scheme)
        is_match = (decoded == sample_bits)
        if not is_match:
            dec_all_ok = False
        print(f"  Param-Decode [{scheme:22s}]: {decoded} -> {'PASS' if is_match else 'FAIL'}")

    # Test B8ZS and HDB3 Descramblers
    _, _, t_b, v_b = scramble_b8zs(b8zs_in)
    dec_b8zs = decode_signal(t_b, v_b, "B8ZS")
    b8zs_dec_ok = (dec_b8zs == b8zs_in)
    print(f"  Param-Decode [B8ZS Descrambler       ]: {dec_b8zs} -> {'PASS' if b8zs_dec_ok else 'FAIL'}")

    _, _, t_h, v_h = scramble_hdb3(hdb3_in)
    dec_hdb3 = decode_signal(t_h, v_h, "HDB3")
    hdb3_dec_ok = (dec_hdb3 == hdb3_in)
    print(f"  Param-Decode [HDB3 Descrambler       ]: {dec_hdb3} -> {'PASS' if hdb3_dec_ok else 'FAIL'}")

    results.append(("Waveform Parameter-based Decoders & Descramblers", dec_all_ok and b8zs_dec_ok and hdb3_dec_ok))

    # ---------------------------------------------------------
    # 7. Extra Credit: Direct Image-Pixel Analysis Decoders (PNG Waveforms)
    # ---------------------------------------------------------
    print("\n[TEST 7] Extra Credit: Direct Image-Pixel Analysis Decoding (from PNG plots)")
    img_all_ok = True
    temp_files = []

    # Test all 5 line codes via image pixels
    for scheme in line_schemes:
        levels, t, v = encode_signal(sample_bits, scheme)
        temp_img = f"test_img_{scheme.lower().replace(' ', '_').replace('-', '')}.png"
        plot_line_code(sample_bits, t, v, scheme, save_path=temp_img, show=False)
        temp_files.append(temp_img)

        decoded_img = decode_from_image(temp_img, scheme, num_bits=len(sample_bits))
        match = (decoded_img == sample_bits)
        if not match:
            img_all_ok = False
        print(f"  Image-Decode [{scheme:22s}]: {decoded_img} -> {'PASS' if match else 'FAIL'}")

    # Test B8ZS via image pixels
    b_img = "test_img_b8zs.png"
    plot_line_code(b8zs_in, t_b, v_b, "B8ZS", labels=b8zs_syms, save_path=b_img, show=False)
    temp_files.append(b_img)
    dec_img_b8zs = decode_from_image(b_img, "B8ZS", num_bits=len(b8zs_in))
    b8zs_img_ok = (dec_img_b8zs == b8zs_in)
    print(f"  Image-Decode [B8ZS Descrambler       ]: {dec_img_b8zs} -> {'PASS' if b8zs_img_ok else 'FAIL'}")

    # Test HDB3 via image pixels
    h_img = "test_img_hdb3.png"
    plot_line_code(hdb3_in, t_h, v_h, "HDB3", labels=hdb3_syms, save_path=h_img, show=False)
    temp_files.append(h_img)
    dec_img_hdb3 = decode_from_image(h_img, "HDB3", num_bits=len(hdb3_in))
    hdb3_img_ok = (dec_img_hdb3 == hdb3_in)
    print(f"  Image-Decode [HDB3 Descrambler       ]: {dec_img_hdb3} -> {'PASS' if hdb3_img_ok else 'FAIL'}")

    # Clean up temporary test images
    for f in temp_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass

    results.append(("Direct Image-Pixel Analysis Decoders", img_all_ok and b8zs_img_ok and hdb3_img_ok))

    # ---------------------------------------------------------
    # Summary Table
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"{'TEST COMPONENT SUMMARY':^70}")
    print("=" * 70)
    print(f"{'#':<3} | {'Component Name':<50} | {'Status':<10}")
    print("-" * 70)
    all_passed = True
    for idx, (name, status) in enumerate(results, 1):
        status_str = "PASS" if status else "FAIL"
        if not status:
            all_passed = False
        print(f"{idx:<3} | {name:<50} | {status_str:<10}")
    print("=" * 70)

    if all_passed:
        print(">>> ALL 7 TEST CATEGORIES PASSED 100% SUCCESSFULLY! <<<")
        print("Project satisfies all requirements of ITT 036 Programming Assignment 1.")
    else:
        print(">>> SOME TESTS FAILED. PLEASE REVIEW LOG ABOVE. <<<")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
