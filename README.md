# ITT 036 — Programming Assignment 1: Digital Signal Encoder & Decoder

![Course](https://img.shields.io/badge/Course-ITT%20036%20Autumn%202026-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)
![Tests](https://img.shields.io/badge/Test%20Suite-7%2F7%20Passed%20(100%25)-success.svg)
![Due Date](https://img.shields.io/badge/Due%20Date-21%20October%202026-orange.svg)

**Course:** ITT 036 (Autumn 2026)  
**Assignment:** Programming Assignment 1 — Digital Signal Encoder, Scrambler & Decoder Pipeline  
**Due Date:** 21 October 2026  
**Contributors:**
- **Saurabh Patel**
- **Mohit Moriya**
- **Hemendra Kumar**

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features & Implemented Modules](#-key-features--implemented-modules)
   - [1. Digital Data Generator & Zero Injection](#1-digital-data-generator--zero-injection)
   - [2. Competitive Coding: Manacher's Algorithm O(N)](#2-competitive-coding-manachers-algorithm-on)
   - [3. Digital Line Coding Schemes](#3-digital-line-coding-schemes)
   - [4. AMI Scrambling Schemes & Zero-Run O(N)](#4-ami-scrambling-schemes--zero-run-on)
   - [5. Analog-to-Digital Modulation (PCM & DM)](#5-analog-to-digital-modulation-pcm--dm)
   - [6. Extra Credit: Waveform & Image-Pixel Decoders](#6-extra-credit-waveform--image-pixel-decoders)
   - [7. Extra Credit: Desktop GUI Visualizer](#7-extra-credit-desktop-gui-visualizer)
3. [Project Architecture](#-project-architecture)
4. [Installation & Setup](#-installation--setup)
5. [Execution Guide](#-execution-guide)
6. [🧪 Complete Automated Test Results](#-complete-automated-test-results)
7. [Gradescope Submission Checklist](#-gradescope-submission-checklist)
8. [References](#-references)

---

## 📌 Project Overview
This repository contains a full-featured, modular digital communication simulation system built in pure Python (non-MATLAB) in compliance with the **Autumn 2026 ITT 036 Programming Assignment 1** guidelines.

The pipeline spans the entire digital signaling flow:
- Input handling (both raw bitstreams and continuous sinusoidal analog inputs)
- High-efficiency competitive coding algorithms ($O(N)$ linear-time palindrome and zero-run detection)
- Standard physical layer line coding schemes
- Bipolar AMI violation scrambling (B8ZS and HDB3)
- Analog pulse modulation (PCM and 1-bit Delta Modulation) with staircase signal reconstruction
- **Extra Credit**: Signal decoding via physical voltage sampling as well as **direct pixel analysis of generated waveform images** (`decode_from_image`)
- **Extra Credit**: Interactive Tkinter graphical interface for live signal visualization

---

## 🚀 Key Features & Implemented Modules

### 1. Digital Data Generator & Zero Injection
File: [`data_generator.py`](data_generator.py)
- **`generate_random_bits(length)`**: Generates purely random binary streams of arbitrary length.
- **`generate_bits_with_zero_runs(length, run_type)`**: Injects specific zero-run patterns without overlapping:
  - `run_type="4_zeros"` / `"four"`: Injects 4 consecutive zeros (`0000`) required for HDB3 scrambling.
  - `run_type="8_zeros"` / `"eight"`: Injects 8 consecutive zeros (`00000000`) required for B8ZS scrambling.
  - `run_type="both"`: Injects both 8-zero and 4-zero sequences in distinct non-overlapping segments.
- **`generate_and_find_palindrome(length, run_type)`**: Direct assignment-level integration returning both the generated bitstream and its longest palindromic substring.
- **`format_bitstream(bits)`**: Formats raw streams into 4-bit nibbles (e.g. `1011 0010`) for human readability.

### 2. Competitive Coding: Manacher's Algorithm $O(N)$
File: [`palindrome.py`](palindrome.py)
- **Problem Requirement:** Identify the longest palindromic sequence in the bitstream. Brute-force ($O(N^3)$) or massive `if/else` ladders receive zero credit.
- **Optimal Implementation:** Implemented using **Manacher's Algorithm** with linear time complexity $O(N)$:
  - Intersperses delimiter characters (`#`) so odd and even palindromes are handled identically.
  - Maintains current center $C$ and rightmost boundary $R$.
  - Reuses mirror symmetry $i' = 2C - i$ to expand palindromes without re-comparing characters.
- **Time Complexity:** $\mathcal{O}(N)$ linear time.
- **Space Complexity:** $\mathcal{O}(N)$ auxiliary space.

### 3. Digital Line Coding Schemes
File: [`line_coding.py`](line_coding.py)  
Implements all 5 standard line coding techniques with normalized voltage levels ($+1\text{ V}, -1\text{ V}, 0\text{ V}$):

| Scheme | Bit `0` Rule | Bit `1` Rule | Mid-Bit Transition? | DC Component |
|---|---|---|:---:|:---:|
| **NRZ-L** | Positive voltage ($+1\text{ V}$) | Negative voltage ($-1\text{ V}$) | No | High |
| **NRZ-I** | No transition at bit boundary | Invert voltage level at bit start | No | High |
| **Manchester (IEEE 802.3)** | High-to-Low ($+1\text{ V} \to -1\text{ V}$) | Low-to-High ($-1\text{ V} \to +1\text{ V}$) | Yes (always) | Zero (DC Balanced) |
| **Differential Manchester** | Transition at start of bit | No transition at start of bit | Yes (Clock sync) | Zero (DC Balanced) |
| **AMI** | Zero voltage ($0\text{ V}$) | Alternating positive ($+1\text{ V}$) & negative ($-1\text{ V}$) | No | Zero (DC Balanced) |

### 4. AMI Scrambling Schemes & Zero-Run $O(N)$
File: [`scrambling.py`](scrambling.py)
- **`find_longest_zero_run(bitstream)`**: Competitive coding component finding the longest contiguous run of zeros in $O(N)$ single-pass linear time with $O(1)$ auxiliary space.
- **B8ZS (Bipolar with 8-Zero Substitution)**:
  - Detects `00000000` and replaces it with `000VB0VB`.
  - $V$ = Bipolar Violation (same polarity as last pulse).
  - $B$ = Bipolar Balancing Pulse (opposite polarity).
- **HDB3 (High-Density Bipolar 3-Zero)**:
  - Detects `0000` and counts pulses since last substitution:
    - **Odd Pulses:** Substitutes `000V` ($V$ matches polarity of previous non-zero pulse).
    - **Even Pulses:** Substitutes `B00V` ($B$ inverts polarity; $V$ matches $B$'s polarity).

### 5. Analog-to-Digital Modulation (PCM & DM)
File: [`modulation.py`](modulation.py)
- **Analog Signal Generator**: Emulates continuous sinusoidal signal ($f = 2\text{ Hz}$) with high-density time sampling.
- **Pulse Code Modulation (PCM)**:
  - Quantizes analog dynamic range into $L = 2^n$ uniform bins (default: $n = 3$, $L = 8$ levels).
  - Encodes each sample into an $n$-bit binary codeword.
  - Reconstructs quantized staircase voltage levels at decoder.
- **Delta Modulation (DM)**:
  - 1-bit differential modulation with configurable step size $\delta$ (default: $0.25\text{ V}$).
  - Outputs `'1'` (step up) or `'0'` (step down) based on staircase approximation.
  - Decoder reconstructs staircase signal tracking original waveform.
- **Pipeline Integration**: The modulated digital bitstream feeds directly into Line Coding encoders as specified in the assignment PDF.

### 6. Extra Credit: Waveform & Image-Pixel Decoders
File: [`decoder.py`](decoder.py)
- **Physical Parameter Decoding**: Reconstructs bitstream strictly from $(t, v)$ voltage samples and boundary derivatives without reading raw bit memory.
- **Direct Image-Pixel Analysis Decoding (`decode_from_image`)**:
  - Directly fulfills the PDF guideline: *"decode the signal by analysing the encoded signal parameters (i.e., image) and not the direct data values."*
  - Reads saved waveform PNG images (`plt.imread`).
  - Segments the blue signal trace pixels (`#0066cc`) using RGB thresholding.
  - Derives bounding boxes, centers, and voltage transitions per bit interval.
  - Reconstructs binary streams with 100% fidelity.
- **B8ZS & HDB3 Descramblers**:
  - Automatically detects violation pulses ($V$) and balancing pulses ($B$) to reverse substitution patterns back to original `'0'` runs.

### 7. Extra Credit: Desktop GUI Visualizer
File: [`gui.py`](gui.py)
- Native desktop application implemented in **Tkinter + Matplotlib**.
- Tab 1: **Digital Line Coding Visualizer** with live bitstream generation, palindrome inspection, zero-run viewer, radiobutton scheme selectors, waveform plotting, and one-click decode verification.
- Tab 2: **Analog Modulation Visualizer** with sine wave generation, PCM quantization level sliders, DM step size controls, and staircase reconstruction.

---

## 📂 Project Architecture

```text
Data_Com_Assignment/
├── README.md               # Complete project documentation & results log
├── requirements.txt        # Dependencies: numpy, matplotlib
├── SPECIFICATION_REPORT.md # 1-Page specification report for Gradescope
├── data_generator.py       # Random bitstream & zero-run sequence generator
├── palindrome.py           # O(N) Manacher's palindrome detection algorithm
├── line_coding.py          # 5 Standard digital line coding encoders
├── scrambling.py           # AMI Scrambling (B8ZS, HDB3) & zero-run O(N)
├── modulation.py           # PCM and Delta Modulation encoders/decoders
├── decoder.py              # Parameter & direct Image-pixel analysis decoders
├── plotter.py              # Visual waveform & staircase signal plotter
├── gui.py                  # Interactive desktop Tkinter GUI visualizer
├── main.py                 # Central interactive CLI pipeline
└── test_suite.py           # Comprehensive automated test suite
```

---

## 🛠️ Installation & Setup

Make sure Python 3.8+ is installed on your machine.

```bash
# 1. Clone repository
git clone https://github.com/star100rabh/Data_Com_Assignment.git
cd Data_Com_Assignment

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On macOS / Linux
# or: .venv\Scripts\activate    # On Windows

# 3. Install required libraries
pip install -r requirements.txt
```

---

## 💻 Execution & Testing Guide

### 1. Interactive CLI Pipeline (Assignment Prompt Flow)
Executes the exact sequence of queries specified in Page 1 of the assignment PDF:
```bash
python3 main.py
```
**Interactive Sequence:**
1. Choose **Digital Input** or **Analog Input (PCM/DM)**.
2. For Digital: Enter custom bitstream or auto-generate (Random / 4-zeros / 8-zeros).
3. System automatically calculates and displays the **Longest Palindromic Sequence** ($O(N)$ Manacher).
4. Select Line Coding scheme (NRZ-L, NRZ-I, Manchester, Differential Manchester, AMI).
5. If AMI: Prompts whether scrambling is needed, and choice of **B8ZS** or **HDB3**.
6. Waveform plot is generated and saved.
7. Prompts: `[Extra Credit] Do you want to decode the signal? (yes/no)`.
8. System performs **both physical parameter decoding and direct PNG image-pixel decoding**, showing verification status.

### 2. Desktop Graphical User Interface (GUI)
To launch the interactive visualizer application:
```bash
python3 gui.py
# or via main launcher:
python3 main.py --gui
```

### 3. Automated Verification Test Suite
Executes the comprehensive automated test suite across all 7 assignment components:
```bash
python3 test_suite.py
```

### 4. Standalone Module Verification Checks
Each module can also be tested independently with its self-contained verification block:
```bash
# Test bitstream generator & zero-run injection
python3 data_generator.py

# Test O(N) Manacher's palindrome detection algorithm
python3 palindrome.py

# Test line coding encoders (NRZ-L, NRZ-I, Manchester, Diff Manchester, AMI)
python3 line_coding.py

# Test AMI scramblers (B8ZS & HDB3) with O(N) zero-run detection
python3 scrambling.py

# Test analog PCM quantization & Delta Modulation (DM)
python3 modulation.py

# Test physical waveform parameter & PNG image-pixel decoders
python3 decoder.py

# Test waveform plotting utilities
python3 plotter.py
```

---

## 🧪 Complete Automated Test Results

The test suite [`test_suite.py`](test_suite.py) was executed to validate every component described in the assignment specification.

### Summary Table

| # | Component / Requirement | Test Description | Complexity | Result |
|:---:|---|---|:---:|:---:|
| **1** | **Digital Data Generator** | 24-bit random streams, 4-zero injection (HDB3), 8-zero injection (B8ZS), dual injection, and direct generator+palindrome integration | $O(N)$ | **PASS (100%)** |
| **2** | **Competitive Palindrome Detection** | Evaluates odd/even palindromes (`0110`, `10101`, 32-bit streams) using Manacher's Algorithm | $O(N)$ | **PASS (100%)** |
| **3** | **Line Coding Encoders** | Encodes test bitstreams with NRZ-L, NRZ-I, Manchester, Differential Manchester, and AMI | $O(N)$ | **PASS (100%)** |
| **4** | **AMI Scrambling & Zero-Run** | Single-pass zero-run detection, B8ZS substitution (`000VB0VB`), and HDB3 odd/even pulse substitutions | $O(N)$ | **PASS (100%)** |
| **5** | **Analog Modulation (PCM & DM)** | Generates analog sine wave; quantizes and encodes PCM with staircase decode; 1-bit DM step tracking | $O(N)$ | **PASS (100%)** |
| **6** | **Waveform Parameter Decoders** | Decodes all 5 line codes and B8ZS/HDB3 descramblers strictly from physical $(t, v)$ arrays | $O(N)$ | **PASS (100%)** |
| **7** | **Direct Image-Pixel Decoders** | Loads saved PNG plot images, segments waveform trace pixels, and reconstructs original bitstreams | $O(\text{Pixels})$ | **PASS (100%)** |

**Overall Status:** `7 / 7 Categories Passed (100% Success Rate)`.

---

### Detailed Test Execution Log

```text
======================================================================
 ITT 036: COMPREHENSIVE AUTOMATED TEST SUITE
======================================================================

[TEST 1] Digital Data Generator & Zero Sequence Injection
  Random bits (24b)            : 000110110000011110011010 [PASS]
  Injected 4 zeros (HDB3)      : 101111100000001110001010 [PASS]
  Injected 8 zeros (B8ZS)      : 1010000001111100000000000001 [PASS]
  Injected both (B8ZS + HDB3)  : 11110000000010000100000001001110 [PASS]
  Generator + Palindrome direct: 10110000001101 (len 14) [PASS]

[TEST 2] Competitive Coding: Manacher's O(N) Palindrome Detection
  Input: 0110                             -> Detected: 0110             [PASS]
  Input: 10101                            -> Detected: 10101            [PASS]
  Input: 00101011100010111101111100001111 -> Detected: 111100001111     [PASS]
  Input: 111111                           -> Detected: 111111           [PASS]
  Input: 1000000001                       -> Detected: 1000000001       [PASS]

[TEST 3] Line Coding Encoders (All 5 Standard Schemes)
  Encoding NRZ-L                  : Discrete levels count =  7 [PASS]
  Encoding NRZ-I                  : Discrete levels count =  7 [PASS]
  Encoding Manchester             : Discrete levels count = 14 [PASS]
  Encoding Differential Manchester: Discrete levels count = 14 [PASS]
  Encoding AMI                    : Discrete levels count =  7 [PASS]

[TEST 4] AMI Scrambling Schemes (B8ZS, HDB3) & O(N) Zero-Run
  Longest Zero-Run Detection   : Length=8, Start=7 [PASS]
  B8ZS Scrambler (000VB0VB)    : Symbols=+ - 0 0 0 V- B+ 0... [PASS]
  HDB3 Scrambler (000V/B00V)   : Symbols=+ 0 0 0 V+ - + B- 0 0 V- [PASS]

[TEST 5] Analog Modulation: PCM and Delta Modulation (DM)
  PCM (3-bit, 24 samples)      : Encoded 72 bits, Decoder match=True [PASS]
  Delta Modulation (DM)        : Encoded 24 bits, Decoder match=True [PASS]

[TEST 6] Extra Credit: Physical Waveform Parameter Decoders
  Param-Decode [NRZ-L                 ]: 1011001 -> PASS
  Param-Decode [NRZ-I                 ]: 1011001 -> PASS
  Param-Decode [Manchester            ]: 1011001 -> PASS
  Param-Decode [Differential Manchester]: 1011001 -> PASS
  Param-Decode [AMI                   ]: 1011001 -> PASS
  Param-Decode [B8ZS Descrambler       ]: 110000000010 -> PASS
  Param-Decode [HDB3 Descrambler       ]: 10000110000 -> PASS

[TEST 7] Extra Credit: Direct Image-Pixel Analysis Decoding (from PNG plots)
  Image-Decode [NRZ-L                 ]: 1011001 -> PASS
  Image-Decode [NRZ-I                 ]: 1011001 -> PASS
  Image-Decode [Manchester            ]: 1011001 -> PASS
  Image-Decode [Differential Manchester]: 1011001 -> PASS
  Image-Decode [AMI                   ]: 1011001 -> PASS
  Image-Decode [B8ZS Descrambler       ]: 110000000010 -> PASS
  Image-Decode [HDB3 Descrambler       ]: 10000110000 -> PASS

======================================================================
                        TEST COMPONENT SUMMARY                        
======================================================================
#   | Component Name                                     | Status    
----------------------------------------------------------------------
1   | Digital Data Generator & Injection                 | PASS      
2   | Manacher's Palindrome Detection O(N)               | PASS      
3   | 5 Line Coding Encoders                             | PASS      
4   | B8ZS & HDB3 Scramblers + Zero-Run O(N)             | PASS      
5   | PCM & Delta Modulation Encoders/Decoders           | PASS      
6   | Waveform Parameter-based Decoders & Descramblers   | PASS      
7   | Direct Image-Pixel Analysis Decoders               | PASS      
======================================================================
>>> ALL 7 TEST CATEGORIES PASSED 100% SUCCESSFULLY! <<<
Project satisfies all requirements of ITT 036 Programming Assignment 1.
```

---

### End-to-End Decoding Fidelity Comparison

| Scheme | Original Bitstream | Decoded from Physical Waveform | Decoded from PNG Plot Image | Match Status |
|---|:---:|:---:|:---:|:---:|
| **NRZ-L** | `1011001` | `1011001` | `1011001` | **100% Match** |
| **NRZ-I** | `1011001` | `1011001` | `1011001` | **100% Match** |
| **Manchester** | `1011001` | `1011001` | `1011001` | **100% Match** |
| **Diff Manchester** | `1011001` | `1011001` | `1011001` | **100% Match** |
| **AMI** | `1011001` | `1011001` | `1011001` | **100% Match** |
| **B8ZS Scrambled** | `110000000010` | `110000000010` | `110000000010` | **100% Match** |
| **HDB3 Scrambled** | `10000110000` | `10000110000` | `10000110000` | **100% Match** |

---

## 📋 Gradescope Submission Checklist

As specified in Page 2 of the assignment:
- [x] Complete Python source code adhering to assignment constraints (no MATLAB/Octave).
- [x] [`SPECIFICATION_REPORT.md`](SPECIFICATION_REPORT.md): 1-Page specification report covering languages, libraries, assumptions, execution guide, and academic references.
- [x] All competitive coding components implemented in optimal linear time $O(N)$ without nested `if/else` ladders.
- [x] Extra credit component: Signal decoding from waveform parameters and saved plot images.
- [x] Extra credit component: Interactive desktop graphical user interface (`gui.py`).
- [x] Both code repository and 1-page report prepared for separate submission to Gradescope.

---

## 📚 References
1. B. A. Forouzan, *Data Communications and Networking*, 5th ed., McGraw-Hill, 2012 (Chapter 4: Digital Transmission, Chapter 5: Analog Transmission).
2. IEEE Standard 802.3-2018, *IEEE Standard for Ethernet: Physical Layer and Management Parameters*.
3. G. Manacher, *"A New Linear-Time 'On-Line' Algorithm for Finding the Smallest Initial Palindrome of a String"*, Journal of the ACM, vol. 22, no. 3, pp. 346–351, 1975.
