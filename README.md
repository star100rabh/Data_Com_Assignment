# ITT 036 - Programming Assignment 1: Digital Signal Encoder & Decoder

**Course:** ITT 036 (Autumn 2026)  
**Project:** Digital Signal Encoder, Scrambler & Decoder Implementation  
**Submission Due Date:** 21 October 2026  
**Contributors:**  
- Saurabh Patel
- Mohit Moriya
- Hemendra Kumar

---

## 📌 Project Overview
This project implements a complete, end-to-end digital communication pipeline complying with all requirements of ITT 036 Programming Assignment 1:

1. **Digital Data Generator**:
   - Generates purely random binary streams.
   - Generates bitstreams with injected runs of consecutive zeros (4-zero sequences for HDB3, 8-zero sequences for B8ZS, or both).
   - Direct integration returning both bitstream and its longest palindromic sequence.
2. **Competitive Coding Components ($O(N)$ Optimal Algorithms)**:
   - **Longest Palindromic Sequence Detection**: Implemented with **Manacher's Algorithm** in optimal linear $O(N)$ time, avoiding nested if-else ladders and brute-force loops.
   - **Longest Common Sequence of Zeros**: Implemented with a linear $O(N)$ single-pass algorithm.
3. **5 Standard Line Coding Schemes**:
   - Non-Return-to-Zero Level (NRZ-L)
   - Non-Return-to-Zero Inverted (NRZ-I)
   - Manchester (IEEE 802.3 standard)
   - Differential Manchester
   - Alternate Mark Inversion (AMI)
4. **Scrambling Techniques (AMI)**:
   - **B8ZS** (Bipolar with 8-Zero Substitution): Replaces `00000000` with `000VB0VB`.
   - **HDB3** (High-Density Bipolar 3-Zero): Replaces `0000` with `000V` (odd pulses) or `B00V` (even pulses).
5. **Analog-to-Digital Modulation Schemes**:
   - **Pulse Code Modulation (PCM)**: Continuous signal sampling, quantization into $2^n$ levels, binary codeword encoding, and quantized staircase reconstruction.
   - **Delta Modulation (DM)**: 1-bit staircase approximation ($+\delta / -\delta$) and decoder reconstruction.
   - Modulated digital bitstreams directly fed into Line Coding as required.
6. **Extra Credit: Line Coding Decoders & Descramblers**:
   - **Physical Waveform Parameter Decoding**: Reconstructs bitstreams strictly by sampling voltage levels and boundary transitions from the physical waveform arrays $(t, v)$, without reading data values.
   - **Direct Image-Pixel Analysis Decoding**: Analyzes pixels of saved waveform PNG plots (`decode_from_image`) to detect trace positions, voltage levels, and transitions, directly fulfilling the PDF prompt: *"decode the signal by analysing the encoded signal parameters (i.e., image) and not the direct data values."*
7. **Extra Credit: Graphical Visualizer GUI**:
   - Interactive Tkinter desktop GUI (`gui.py`) for live waveform plotting, modulation analysis, and signal comparison.

---

## 🛠️ Requirements & Setup
Make sure Python 3.8+ is installed. Install required packages using:
```bash
pip install -r requirements.txt
```
Or use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 Project Structure
```text
Data_Com_Assignment/
├── README.md               # Complete project documentation & results log
├── requirements.txt        # Python package dependencies (numpy, matplotlib)
├── SPECIFICATION_REPORT.md # 1-Page specification report for Gradescope
├── data_generator.py       # Bitstream generation & zero-run sequence injection
├── palindrome.py           # O(N) Manacher's palindrome detection algorithm
├── line_coding.py          # 5 Line coding encoders (NRZ-L, NRZ-I, Manchester, etc.)
├── scrambling.py           # AMI Scrambling schemes (B8ZS, HDB3) & zero-run O(N)
├── modulation.py           # PCM and Delta Modulation encoders, decoders & staircase
├── decoder.py              # Extra Credit: Parameter & direct Image-pixel decoders
├── plotter.py              # Matplotlib visual waveform & staircase visualizer
├── gui.py                  # Extra Credit: Interactive Tkinter desktop GUI
├── main.py                 # Main interactive CLI pipeline matching assignment flow
└── test_suite.py           # Comprehensive automated test suite for all modules
```

---

## 🚀 Execution Guide

### 1. Main Interactive CLI Pipeline (Assignment Prompt Flow)
Follows the exact question sequence specified in Page 1 of the assignment PDF:
```bash
python main.py
```
- Prompts for **Digital Input** (custom or generated) or **Analog Input** (PCM/DM).
- Computes the **Longest Palindromic Sequence** ($O(N)$ Manacher's algorithm).
- Prompts for Line Coding scheme (NRZ-L, NRZ-I, Manchester, Differential Manchester, AMI).
- If AMI is selected: prompts whether scrambling is needed, and choice of **B8ZS** or **HDB3**.
- Saves waveform plot image and prompts: *"Do you want to decode the signal? (yes/no)"*.
- Decodes the signal via both physical waveform sampling and direct image pixel analysis.

### 2. Desktop Graphical User Interface (GUI)
```bash
python main.py --gui
# or directly:
python gui.py
```

### 3. Automated Verification Test Suite
Runs all 7 test categories across every module and prints verification results:
```bash
python test_suite.py
```

### 4. Standalone Module Verification Checks
Each module contains its own self-test block:
```bash
python data_generator.py
python palindrome.py
python line_coding.py
python scrambling.py
python modulation.py
python decoder.py
```

---

## 🧪 Automated Test Verification Results

All components were tested and validated with the automated test suite (`python test_suite.py`):

| # | Test Component | Requirements Covered | Status |
|---|---|---|---|
| **1** | **Digital Data Generator** | Random bitstream, 4-zero injection (HDB3), 8-zero injection (B8ZS), formatting, direct palindrome integration | **PASS** (100%) |
| **2** | **Competitive Palindrome Detection** | Optimal $O(N)$ Manacher's algorithm on odd/even palindromes & long bitstreams | **PASS** (100%) |
| **3** | **Line Coding Encoders** | NRZ-L, NRZ-I, Manchester (IEEE 802.3), Differential Manchester, AMI | **PASS** (100%) |
| **4** | **AMI Scrambling & Zero-Run** | B8ZS (`000VB0VB`), HDB3 (odd/even substitutions), $O(N)$ zero-run detection | **PASS** (100%) |
| **5** | **Analog Modulation (PCM & DM)** | Continuous signal sampling, PCM quantization & codeword encoding, DM 1-bit delta, decoder staircase reconstruction | **PASS** (100%) |
| **6** | **Waveform Parameter Decoders** | All 5 line codes decoded from physical $(t, v)$ parameters, B8ZS/HDB3 descramblers | **PASS** (100%) |
| **7** | **Direct Image-Pixel Decoders** | Decodes all 5 line codes and scrambled signals directly from saved PNG plot images | **PASS** (100%) |

**Summary Result:** `7 / 7 Test Categories Passed (100% Success Rate)`.

---

## 📌 Implementation Log
- Implemented bitstream generator and zero-run sequence injection module (`data_generator.py`).
- Implemented Manacher's Algorithm for optimal $O(N)$ longest palindromic sequence detection (`palindrome.py`).
- Implemented NRZ-L and NRZ-I line coding encoders with waveform plotting utility (`line_coding.py`, `plotter.py`).
- Added Manchester (IEEE 802.3), Differential Manchester, and AMI line coding encoders (`line_coding.py`).
- Implemented B8ZS and HDB3 scrambling schemes for AMI with $O(N)$ zero-run sequence analysis (`scrambling.py`).
- Implemented Pulse Code Modulation (PCM) and Delta Modulation (DM) with staircase signal reconstruction (`modulation.py`).
- Implemented waveform parameter-based line coding decoders and AMI descramblers (`decoder.py`).
- Built interactive CLI pipeline (`main.py`) matching assignment prompt sequence and desktop Tkinter GUI visualizer (`gui.py`).
- Prepared complete 1-page specification report (`SPECIFICATION_REPORT.md`) for Gradescope.
- Enhanced `data_generator.py` with flexible sequence injection aliases and direct palindrome integration.
- Added direct **image-pixel analysis decoder** (`decode_from_image`) in `decoder.py` analyzing saved plot images.
- Implemented comprehensive automated test suite (`test_suite.py`) validating all 7 project categories with 100% pass rate.






