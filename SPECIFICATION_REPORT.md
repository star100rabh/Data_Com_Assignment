# ITT 036 — Programming Assignment 1: Specification Report
**Project Title:** Digital Signal Encoder, Scrambler & Decoder Implementation  
**Course:** ITT 036 (Autumn 2026) | **Date:** 21 October 2026  
**Deliverable:** 1-Page Specification Report for Gradescope Submission  

---

## 1. Programming Language & Libraries Used
- **Language:** Python 3.8+ (Non-MATLAB implementation complying with course guidelines).
- **Libraries:**
  - `numpy`: High-resolution continuous time-domain signal arrays, quantization zones, and discrete levels.
  - `matplotlib`: Multi-tier waveform rendering, bit-level annotations, violation color-coding, and staircase plotting.
  - `tkinter`: Native GUI framework for desktop visual interface (Extra credit UI improvement).

---

## 2. System Architecture & Component Mapping
```text
DataCom/
├── data_generator.py      # Random bitstream & 4-zero (HDB3) / 8-zero (B8ZS) sequence injection
├── palindrome.py          # O(N) Manacher's Algorithm for Longest Palindromic Sequence
├── line_coding.py         # Encoders for NRZ-L, NRZ-I, Manchester, Diff Manchester, AMI
├── scrambling.py          # B8ZS & HDB3 scrambling with O(N) zero-run sequence detection
├── modulation.py          # PCM (quantization/encoding) & Delta Modulation (DM) with staircase
├── decoder.py             # Extra Credit: Physical waveform parameter-based decoders & descramblers
├── plotter.py             # Signal visualizer (waveforms, staircase, and violation highlights)
├── gui.py                 # Extra Credit: Interactive graphical desktop visualizer (Tkinter + Matplotlib)
└── main.py                # Unified interactive CLI pipeline matching PDF decision flow
```

---

## 3. Assumptions Considered
1. **Voltage Levels:** Signals are normalized to standard bipolar levels: $+V = +1\text{ V}$, $-V = -1\text{ V}$, and $0\text{ V}$.
2. **Timing & Resolution:** Normalized bit interval $T_b = 1.0\text{ s}$. Each bit interval is discretized into 100 continuous samples ($100\text{ samples/bit}$) to emulate physical analog waveforms.
3. **Initial Reference States:**
   - **NRZ-I & Differential Manchester:** Assume an initial pre-transmission voltage level of $+1\text{ V}$.
   - **AMI:** Alternating polarity tracking begins with negative polarity so the first data `'1'` produces $+1\text{ V}$.
4. **Physical Waveform Decoding (Extra Credit):** Receivers analyze voltage thresholds ($V > 0 \implies '0'$, $V < 0 \implies '1'$ for NRZ-L) and transition derivatives across boundaries (Manchester and NRZ-I) strictly from physical $(t, v)$ samples, without reading data bit memory.
5. **B8ZS & HDB3 Descrambling:** Receivers inspect AMI violation polarity ($V$, where current pulse matches previous pulse polarity) to reverse substitutions back to pure `'0'`s.

---

## 4. Competitive Coding Complexity Analysis
- **Longest Palindrome Detection:** Implemented using **Manacher's Algorithm**. By inserting `#` delimiters and exploiting palindrome center-mirror symmetry $(2C - i)$, comparisons are never repeated. **Time Complexity: $O(N)$ linear time**, **Space Complexity: $O(N)$**. (Massive if/else or brute-force $O(N^3)/O(N^2)$ avoided).
- **Longest Zero-Run Detection:** Implemented using a single-pass tracking window. **Time Complexity: $O(N)$**, **Auxiliary Space: $O(1)$**.

---

## 5. How to Run the Code
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the main interactive CLI pipeline (Teacher's prompt flow)
python main.py

# 3. Launch the graphical user interface (Extra Credit visualizer)
python main.py --gui   # or: python gui.py

# 4. Run standalone test checks for any module
python data_generator.py | python palindrome.py | python line_coding.py
python scrambling.py     | python modulation.py  | python decoder.py
```

---

## 6. References
1. B. A. Forouzan, *Data Communications and Networking*, 5th ed., McGraw-Hill, 2012 (Chapters 4 & 5).
2. IEEE Standard 802.3-2018, *Ethernet: Physical Layer and Management Parameters*.
3. G. Manacher, *"A New Linear-Time 'On-Line' Algorithm for Finding the Smallest Initial Palindrome of a String"*, J. ACM, vol. 22, no. 3, pp. 346–351, 1975.
