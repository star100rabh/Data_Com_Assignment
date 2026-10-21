"""
palindrome.py
Competitive Coding Component:
Finds the longest palindromic sequence in a binary bitstream.

Implemented using Manacher's Algorithm for optimal O(N) linear time complexity,
avoiding nested if-else ladders and brute-force O(N^3) or O(N^2) checks.
"""


def longest_palindrome_manacher(bitstream: str) -> str:
    """
    Finds the longest palindromic substring in O(N) time using Manacher's algorithm.

    How it works:
    1. Preprocesses string with '#' between characters (e.g. '1001' -> '^#1#0#0#1#$')
       so odd and even length palindromes are handled uniformly.
    2. Maintains current center (C) and right boundary (R) of the furthest palindrome.
    3. Reuses previously computed palindrome radii using mirror symmetry (2*C - i),
       which avoids redundant comparisons and ensures linear O(N) execution.
    """
    if not bitstream:
        return ""
    if len(bitstream) == 1:
        return bitstream

    # Step 1: Preprocessing with delimiters
    # '^' and '$' act as sentinel bounds to avoid index out-of-range checks
    transformed = "^#" + "#".join(bitstream) + "#$"
    n = len(transformed)

    # P[i] stores the radius of palindrome centered at transformed[i]
    p = [0] * n
    c = 0  # Center of palindrome with current furthest right boundary
    r = 0  # Furthest right boundary reached so far

    for i in range(1, n - 1):
        i_mirror = 2 * c - i  # Mirror of index i with respect to center c

        # If i is within current boundary, initialize with mirror value
        if r > i:
            p[i] = min(r - i, p[i_mirror])
        else:
            p[i] = 0

        # Expand palindrome around center i while characters match
        while transformed[i + 1 + p[i]] == transformed[i - 1 - p[i]]:
            p[i] += 1

        # If expanded past current right boundary, update center and boundary
        if i + p[i] > r:
            c = i
            r = i + p[i]

    # Find the maximum radius in P
    max_len = 0
    center_idx = 0
    for i in range(1, n - 1):
        if p[i] > max_len:
            max_len = p[i]
            center_idx = i

    # Map back from transformed indices to original bitstream indices
    # Each character in original string maps to: (transformed_index - 1 - max_len) // 2
    start_idx = (center_idx - 1 - max_len) // 2
    return bitstream[start_idx:start_idx + max_len]


def find_longest_palindrome_info(bitstream: str) -> dict:
    """
    Returns a dictionary with the longest palindrome substring, its length,
    and its starting index in the given bitstream.
    """
    palindrome = longest_palindrome_manacher(bitstream)
    start_idx = bitstream.find(palindrome) if palindrome else -1

    return {
        "palindrome": palindrome,
        "length": len(palindrome),
        "start_index": start_idx
    }


if __name__ == "__main__":
    from data_generator import generate_random_bits, generate_bits_with_zero_runs

    print("--- Palindrome Detection Check (Manacher's Algorithm - O(N)) ---")

    # Test 1: Fixed test case with known palindrome (e.g. '10101' or '0110')
    sample_stream = "0110100101100"
    result1 = find_longest_palindrome_info(sample_stream)
    print("\n[Test 1] Fixed sample stream:")
    print("Stream            :", sample_stream)
    print("Longest Palindrome:", result1["palindrome"])
    print("Length            :", result1["length"])
    print("Start Index       :", result1["start_index"])

    # Test 2: Checking on a random bitstream
    random_stream = generate_random_bits(32)
    result2 = find_longest_palindrome_info(random_stream)
    print("\n[Test 2] Random bitstream (32 bits):")
    print("Stream            :", random_stream)
    print("Longest Palindrome:", result2["palindrome"])
    print("Length            :", result2["length"])
    print("Start Index       :", result2["start_index"])

    # Test 3: Checking on sequence with 8 consecutive zeros (all 0s is a palindrome)
    zero_stream = generate_bits_with_zero_runs(28, run_type="eight")
    result3 = find_longest_palindrome_info(zero_stream)
    print("\n[Test 3] Stream with 8-zero run:")
    print("Stream            :", zero_stream)
    print("Longest Palindrome:", result3["palindrome"])
    print("Length            :", result3["length"])

