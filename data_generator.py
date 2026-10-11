"""
data_generator.py
Helper functions to generate random bit sequences and test patterns.
"""

import random


def generate_random_bits(length: int = 16) -> str:
    """
    Generates a random sequence of binary digits (0s and 1s).
    """
    if length <= 0:
        return ""
    
    bits = [str(random.randint(0, 1)) for _ in range(length)]
    return "".join(bits)


def inject_subsequence(base_sequence: str, subseq: str, start_index: int) -> str:
    """
    Injects a specific sub-sequence into a base sequence at a given starting index.
    """
    seq_list = list(base_sequence)
    end_index = start_index + len(subseq)
    
    if end_index <= len(seq_list):
        seq_list[start_index:end_index] = list(subseq)
        
    return "".join(seq_list)


def generate_bits_with_zero_runs(length: int = 32, run_type: str = "both") -> str:
    """
    Generates a bit sequence containing runs of consecutive zeros.
    - 'four': inserts 4 consecutive zeros (for HDB3)
    - 'eight': inserts 8 consecutive zeros (for B8ZS)
    - 'both': inserts both patterns
    """
    if run_type == "eight" and length < 10:
        length = 10
    elif run_type == "both" and length < 20:
        length = 20
    elif run_type == "four" and length < 6:
        length = 6

    bits = list(generate_random_bits(length))

    if run_type == "four":
        idx = random.randint(1, length - 5)
        bits[idx:idx + 4] = list("0000")

    elif run_type == "eight":
        idx = random.randint(1, length - 9)
        bits[idx:idx + 8] = list("00000000")

    elif run_type == "both":
        idx1 = random.randint(1, max(1, (length // 2) - 8))
        bits[idx1:idx1 + 8] = list("00000000")

        start_second_half = max(idx1 + 9, length // 2)
        idx2 = random.randint(start_second_half, length - 5)
        bits[idx2:idx2 + 4] = list("0000")

    return "".join(bits)


def format_bitstream(bits: str, group_size: int = 4) -> str:
    """
    Formats a bit sequence into spaced groups (e.g., '1010 0000').
    """
    chunks = [bits[i:i + group_size] for i in range(0, len(bits), group_size)]
    return " ".join(chunks)


# ^^^^^^^^ Test ke liye likha hai maine (START) ^^^^^^^^
# (Yeh section sirf is file ko akele chala kar check karne ke liye hai, main project logic upar hai)
if __name__ == "__main__":
    print("--- Bitstream Generation Check ---")

    # 1. Random bit sequence test
    pure_random = generate_random_bits(length=24)
    print("Random bits (raw)   :", pure_random)
    print("Random bits (visual):", format_bitstream(pure_random))

    # 2. Sequence with 4 consecutive zeros (for HDB3)
    seq_4zeros = generate_bits_with_zero_runs(length=24, run_type="four")
    print("\nSequence with 4 zeros:", seq_4zeros)

    # 3. Sequence with 8 consecutive zeros (for B8ZS)
    seq_8zeros = generate_bits_with_zero_runs(length=28, run_type="eight")
    print("\nSequence with 8 zeros:", seq_8zeros)

    # 4. Sequence with both 4 and 8 zero patterns
    seq_both = generate_bits_with_zero_runs(length=32, run_type="both")
    print("\nSequence with both   :", seq_both)
# ^^^^^^^^ Test ke liye likha hai maine (END) ^^^^^^^^
