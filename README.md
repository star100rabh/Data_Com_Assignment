# ITT 036 - Programming Assignment 1: Digital Signal Encoder & Decoder

**Course:** ITT 036 (Autumn 2026)  
**Project:** Digital Signal Encoder, Scrambler & Decoder Implementation  

---

## 📌 Project Overview
This project implements an end-to-end digital communication pipeline:
1. **Digital Data Generation**: Generates random digital bitstreams and sequences containing injected runs of consecutive zeros (4-zero and 8-zero sequences).
2. **Competitive Palindrome Detection**: Identifies the longest palindromic substring in the bitstream using an optimal $O(N)$ algorithm.
3. **Line Coding Schemes**:
   - Non-Return-to-Zero Level (NRZ-L)
   - Non-Return-to-Zero Inverted (NRZ-I)
   - Manchester
   - Differential Manchester
   - Alternate Mark Inversion (AMI)
4. **Scrambling Techniques (AMI)**:
   - B8ZS (Bipolar with 8-Zero Substitution)
   - HDB3 (High-Density Bipolar 3-Zero)
5. **Modulation Schemes**:
   - Pulse Code Modulation (PCM) with quantization and encoding
   - Delta Modulation (DM) with staircase reconstruction
6. **Waveform Parameter-based Decoding (Extra Credit)**:
   - Reconstructs digital bitstreams strictly by sampling voltage levels and transitions from the physical signal, without reading source bit values.
7. **Interactive GUI / Graphical Visualizer (Extra Credit)**:
   - Visual waveform plotter for inspection and comparison.

---

## 🛠️ Requirements & Setup
Make sure Python 3.8+ is installed. Install required packages using:
```bash
pip install -r requirements.txt
```

---

## 📂 Project Structure
```text
DataCom/
├── README.md
├── requirements.txt
├── data_generator.py      # Bitstream generation & zero-run injection
├── palindrome.py          # O(N) Manacher's palindrome detection
├── line_coding.py         # Digital line coding encoders (NRZ-L, NRZ-I, etc.)
├── scrambling.py          # AMI Scrambling schemes (B8ZS, HDB3)
├── plotter.py             # Signal waveform visualizer
└── ...
```

---

## 📌 Implementation Log
- Implemented bitstream generator and zero-run sequence injection module.
- Implemented Manacher's Algorithm for optimal O(N) longest palindromic sequence detection.
- Implemented NRZ-L and NRZ-I line coding encoders with waveform plotting utility.
- Added Manchester (IEEE 802.3), Differential Manchester, and AMI (Alternate Mark Inversion) line coding encoders.
- Implemented B8ZS and HDB3 scrambling schemes for AMI with O(N) zero-run sequence analysis.




