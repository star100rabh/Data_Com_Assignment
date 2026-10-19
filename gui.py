"""
gui.py
Graphical User Interface (GUI) for ITT 036 Digital Communication Assignment.
Built with Python's native Tkinter and Matplotlib for rich, responsive desktop visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from data_generator import generate_random_bits, generate_bits_with_zero_runs
from palindrome import find_longest_palindrome_info
from line_coding import encode_signal
from scrambling import scramble_b8zs, scramble_hdb3, find_longest_zero_run
from modulation import (
    generate_analog_signal,
    pcm_encode,
    pcm_decode,
    dm_encode,
    dm_decode
)
from decoder import decode_signal


class SignalVisualizerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ITT 036 - Digital Signal Encoder, Scrambler & Decoder")
        self.geometry("1100x760")
        self.minsize(950, 680)

        # State storage
        self.current_time = None
        self.current_voltage = None
        self.current_scheme = "NRZ-L"
        self.last_encoded_bits = ""

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure(bg="#f4f6f9")

        self.style.configure("TNotebook", background="#f4f6f9")
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6])
        self.style.configure("TLabel", background="#f4f6f9", font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#1a365d")
        self.style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), padding=5)

    def _build_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#1a365d", height=45)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        lbl_title = tk.Label(header_frame, text="ITT 036: Digital Signal Encoder, Scrambler & Decoder System",
                             fg="white", bg="#1a365d", font=("Segoe UI", 13, "bold"), pady=8)
        lbl_title.pack()

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tab_digital = ttk.Frame(self.notebook)
        self.tab_analog = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_digital, text=" Line Coding & Scrambling ")
        self.notebook.add(self.tab_analog, text=" Analog Modulation (PCM / DM) ")

        self._build_digital_tab()
        self._build_analog_tab()

    def _build_digital_tab(self):
        # Left control panel
        left_panel = tk.Frame(self.tab_digital, bg="#ffffff", relief=tk.RIDGE, bd=1, width=380)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 10), pady=8)
        left_panel.pack_propagate(False)

        # 1. Bitstream input
        lbl_input = tk.Label(left_panel, text="1. Digital Bitstream Input", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b6cb0")
        lbl_input.pack(anchor="w", padx=10, pady=(10, 4))

        self.entry_bits = ttk.Entry(left_panel, font=("Consolas", 11))
        self.entry_bits.insert(0, "101100101")
        self.entry_bits.pack(fill=tk.X, padx=10, pady=2)

        # Quick generator buttons
        btn_grid = tk.Frame(left_panel, bg="#ffffff")
        btn_grid.pack(fill=tk.X, padx=10, pady=4)

        ttk.Button(btn_grid, text="Random (16b)", command=lambda: self._set_bits(generate_random_bits(16))).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_grid, text="4-Zeros (HDB3)", command=lambda: self._set_bits(generate_bits_with_zero_runs(20, "4_zeros"))).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_grid, text="8-Zeros (B8ZS)", command=lambda: self._set_bits(generate_bits_with_zero_runs(24, "8_zeros"))).grid(row=1, column=0, columnspan=2, padx=2, pady=2, sticky="ew")
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # 2. Competitive analysis box
        lbl_comp = tk.Label(left_panel, text="2. Competitive Analysis (O(N))", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b6cb0")
        lbl_comp.pack(anchor="w", padx=10, pady=(12, 2))

        self.txt_analysis = tk.Text(left_panel, height=4, font=("Consolas", 9), bg="#f7fafc", relief=tk.SOLID, bd=1)
        self.txt_analysis.pack(fill=tk.X, padx=10, pady=2)
        self.txt_analysis.insert(tk.END, "Enter bitstream and encode to see palindrome and zero-run analysis.")
        self.txt_analysis.config(state=tk.DISABLED)

        # 3. Line Coding Scheme Selection
        lbl_scheme = tk.Label(left_panel, text="3. Line Coding Scheme", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b6cb0")
        lbl_scheme.pack(anchor="w", padx=10, pady=(12, 4))

        self.var_scheme = tk.StringVar(value="NRZ-L")
        schemes = ["NRZ-L", "NRZ-I", "Manchester", "Differential Manchester", "AMI"]
        for sch in schemes:
            ttk.Radiobutton(left_panel, text=sch, value=sch, variable=self.var_scheme, command=self._on_scheme_changed).pack(anchor="w", padx=18, pady=1)

        # Scrambling Sub-frame (visible only when AMI is active)
        self.frame_scramble = tk.Frame(left_panel, bg="#edf2f7", relief=tk.GROOVE, bd=1)
        self.frame_scramble.pack(fill=tk.X, padx=10, pady=8)

        lbl_scramble_title = tk.Label(self.frame_scramble, text="AMI Scrambling Option:", font=("Segoe UI", 9, "bold"), bg="#edf2f7")
        lbl_scramble_title.pack(anchor="w", padx=6, pady=(4, 2))

        self.var_scramble = tk.StringVar(value="None")
        for sc in ["None", "B8ZS", "HDB3"]:
            ttk.Radiobutton(self.frame_scramble, text=sc, value=sc, variable=self.var_scramble).pack(anchor="w", padx=16, pady=1)

        # Action Buttons
        btn_encode = tk.Button(left_panel, text="▶  Encode & Plot Waveform", font=("Segoe UI", 10, "bold"),
                               bg="#2b6cb0", fg="white", activebackground="#2c5282", activeforeground="white",
                               command=self.on_encode_digital, relief=tk.FLAT, pady=6)
        btn_encode.pack(fill=tk.X, padx=10, pady=(12, 6))

        btn_decode = tk.Button(left_panel, text="⚡  Decode Waveform (Extra Credit)", font=("Segoe UI", 10, "bold"),
                               bg="#2f855a", fg="white", activebackground="#276749", activeforeground="white",
                               command=self.on_decode_digital, relief=tk.FLAT, pady=6)
        btn_decode.pack(fill=tk.X, padx=10, pady=4)

        # Status text
        self.lbl_status = tk.Label(left_panel, text="Ready", font=("Segoe UI", 9, "italic"), bg="#ffffff", fg="#718096", wraplength=350)
        self.lbl_status.pack(fill=tk.X, padx=10, pady=6)

        # Right canvas area for Matplotlib Waveform
        self.right_frame = tk.Frame(self.tab_digital, bg="#ffffff", relief=tk.RIDGE, bd=1)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=8, padx=5)

        self.fig_digital = Figure(figsize=(7, 4), dpi=100)
        self.canvas_digital = FigureCanvasTkAgg(self.fig_digital, master=self.right_frame)
        self.canvas_digital.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar_digital = NavigationToolbar2Tk(self.canvas_digital, self.right_frame)
        self.toolbar_digital.update()

        # Initial placeholder plot
        self._plot_initial_placeholder()

    def _build_analog_tab(self):
        # Analog Left Panel
        left_panel = tk.Frame(self.tab_analog, bg="#ffffff", relief=tk.RIDGE, bd=1, width=380)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 10), pady=8)
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="1. Analog Modulation Scheme", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b6cb0").pack(anchor="w", padx=10, pady=(10, 4))
        self.var_mod = tk.StringVar(value="PCM")
        ttk.Radiobutton(left_panel, text="Pulse Code Modulation (PCM)", value="PCM", variable=self.var_mod, command=self._toggle_mod_params).pack(anchor="w", padx=16, pady=2)
        ttk.Radiobutton(left_panel, text="Delta Modulation (DM)", value="DM", variable=self.var_mod, command=self._toggle_mod_params).pack(anchor="w", padx=16, pady=2)

        tk.Label(left_panel, text="2. Signal Parameters", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b6cb0").pack(anchor="w", padx=10, pady=(12, 4))

        p_frame = tk.Frame(left_panel, bg="#ffffff")
        p_frame.pack(fill=tk.X, padx=10)

        tk.Label(p_frame, text="Frequency (Hz):", bg="#ffffff").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_freq = ttk.Entry(p_frame, width=8)
        self.entry_freq.insert(0, "2.0")
        self.entry_freq.grid(row=0, column=1, sticky="e", pady=2)

        tk.Label(p_frame, text="Sampling Rate (Hz):", bg="#ffffff").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_fs = ttk.Entry(p_frame, width=8)
        self.entry_fs.insert(0, "24")
        self.entry_fs.grid(row=1, column=1, sticky="e", pady=2)

        self.lbl_pcm_bits = tk.Label(p_frame, text="PCM Quantization Bits:", bg="#ffffff")
        self.lbl_pcm_bits.grid(row=2, column=0, sticky="w", pady=2)
        self.entry_pcm_bits = ttk.Entry(p_frame, width=8)
        self.entry_pcm_bits.insert(0, "3")
        self.entry_pcm_bits.grid(row=2, column=1, sticky="e", pady=2)

        self.lbl_dm_step = tk.Label(p_frame, text="DM Step Size (Delta):", bg="#ffffff")
        self.lbl_dm_step.grid(row=3, column=0, sticky="w", pady=2)
        self.entry_dm_step = ttk.Entry(p_frame, width=8)
        self.entry_dm_step.insert(0, "0.25")
        self.entry_dm_step.grid(row=3, column=1, sticky="e", pady=2)

        # Output Bitstream preview
        tk.Label(left_panel, text="3. Generated Modulated Bitstream", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2b6cb0").pack(anchor="w", padx=10, pady=(12, 2))
        self.txt_mod_bits = tk.Text(left_panel, height=4, font=("Consolas", 9), bg="#f7fafc", relief=tk.SOLID, bd=1)
        self.txt_mod_bits.pack(fill=tk.X, padx=10, pady=2)

        btn_modulate = tk.Button(left_panel, text="▶  Modulate & Plot Staircase", font=("Segoe UI", 10, "bold"),
                                 bg="#2b6cb0", fg="white", activebackground="#2c5282", command=self.on_modulate_analog, relief=tk.FLAT, pady=6)
        btn_modulate.pack(fill=tk.X, padx=10, pady=(12, 6))

        btn_feed_line = tk.Button(left_panel, text="↳  Feed Bitstream to Line Coding Tab", font=("Segoe UI", 9, "bold"),
                                  bg="#6b46c1", fg="white", activebackground="#553c9a", command=self.on_feed_to_line_coding, relief=tk.FLAT, pady=6)
        btn_feed_line.pack(fill=tk.X, padx=10, pady=4)

        # Right canvas area for Analog/Staircase Matplotlib Plot
        right_frame_analog = tk.Frame(self.tab_analog, bg="#ffffff", relief=tk.RIDGE, bd=1)
        right_frame_analog.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=8, padx=5)

        self.fig_analog = Figure(figsize=(7, 4), dpi=100)
        self.canvas_analog = FigureCanvasTkAgg(self.fig_analog, master=right_frame_analog)
        self.canvas_analog.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar_analog = NavigationToolbar2Tk(self.canvas_analog, right_frame_analog)
        self.toolbar_analog.update()

        self._toggle_mod_params()

    def _toggle_mod_params(self):
        if self.var_mod.get() == "PCM":
            self.lbl_pcm_bits.config(state=tk.NORMAL)
            self.entry_pcm_bits.config(state=tk.NORMAL)
            self.lbl_dm_step.config(state=tk.DISABLED)
            self.entry_dm_step.config(state=tk.DISABLED)
        else:
            self.lbl_pcm_bits.config(state=tk.DISABLED)
            self.entry_pcm_bits.config(state=tk.DISABLED)
            self.lbl_dm_step.config(state=tk.NORMAL)
            self.entry_dm_step.config(state=tk.NORMAL)

    def _set_bits(self, bitstream: str):
        self.entry_bits.delete(0, tk.END)
        self.entry_bits.insert(0, bitstream)

    def _on_scheme_changed(self):
        # Enable or highlight scrambling if AMI is chosen
        pass

    def _plot_initial_placeholder(self):
        ax = self.fig_digital.add_subplot(111)
        ax.text(0.5, 0.5, "Click 'Encode & Plot Waveform' to display signal",
                ha="center", va="center", color="gray", fontsize=11)
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas_digital.draw()

    def on_encode_digital(self):
        bitstream = self.entry_bits.get().strip()
        if not bitstream or not all(c in "01" for c in bitstream):
            messagebox.showerror("Invalid Bitstream", "Please enter a valid binary bitstream containing only '0' and '1'.")
            return

        self.last_encoded_bits = bitstream
        scheme = self.var_scheme.get()
        scramble_mode = self.var_scramble.get()

        # Competitive coding calculations
        pal_info = find_longest_palindrome_info(bitstream)
        pal_sub = pal_info["palindrome"]
        pal_len = pal_info["length"]
        pal_start = pal_info["start_index"]
        zero_run = find_longest_zero_run(bitstream)

        # Update analysis box
        self.txt_analysis.config(state=tk.NORMAL)
        self.txt_analysis.delete("1.0", tk.END)
        self.txt_analysis.insert(tk.END, f"Longest Palindrome : {pal_sub} (len={pal_len}, idx={pal_start})\n")
        self.txt_analysis.insert(tk.END, f"Longest Zero-Run   : {zero_run['length']} zeros (from idx {zero_run['start_index']})")
        self.txt_analysis.config(state=tk.DISABLED)

        # Execute encoding
        display_labels = list(bitstream)
        if scheme == "AMI" and scramble_mode in ("B8ZS", "HDB3"):
            if scramble_mode == "B8ZS":
                levels, symbols, time, voltage = scramble_b8zs(bitstream)
            else:
                levels, symbols, time, voltage = scramble_hdb3(bitstream)
            display_labels = symbols
            active_title = f"AMI with {scramble_mode} Scrambling"
            self.current_scheme = scramble_mode
        else:
            levels, time, voltage = encode_signal(bitstream, scheme)
            active_title = f"Line Coding: {scheme}"
            self.current_scheme = scheme

        self.current_time = time
        self.current_voltage = voltage

        # Render on digital Matplotlib canvas
        self.fig_digital.clear()
        ax = self.fig_digital.add_subplot(111)

        num_bits = len(bitstream)
        ax.plot(time, voltage, color="#0066cc", linewidth=2.2, label=f"{active_title}")
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

        for i, lbl in enumerate(display_labels):
            ax.axvline(i, color="lightgray", linestyle=":", linewidth=1)
            box_bg = "#eef5ff"
            box_border = "#99ccff"
            if "V" in str(lbl):
                box_bg = "#ffebee"
                box_border = "#ef5350"
            elif "B" in str(lbl):
                box_bg = "#e8f5e9"
                box_border = "#66bb6a"

            ax.text(i + 0.5, 1.4, str(lbl), fontsize=10, fontweight="bold",
                    ha="center", va="center", color="#333333",
                    bbox=dict(boxstyle="circle,pad=0.2", facecolor=box_bg, edgecolor=box_border))

        ax.axvline(num_bits, color="lightgray", linestyle=":", linewidth=1)
        ax.set_xlim(0, num_bits)
        ax.set_ylim(-1.8, 1.8)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(["-V (-1)", "0 V", "+V (+1)"])
        ax.set_xticks(range(num_bits + 1))
        ax.set_xlabel("Bit Interval (Time)", fontsize=10, fontweight="bold")
        ax.set_ylabel("Voltage Level", fontsize=10, fontweight="bold")
        ax.set_title(active_title, fontsize=12, fontweight="bold")
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)

        self.fig_digital.tight_layout()
        self.canvas_digital.draw()

        self.lbl_status.config(text=f"Encoded {active_title} successfully. Ready to decode.")

    def on_decode_digital(self):
        if self.current_time is None or self.current_voltage is None:
            messagebox.showinfo("No Signal", "Please encode a signal first before decoding.")
            return

        decoded = decode_signal(self.current_time, self.current_voltage, self.current_scheme)
        is_match = (decoded == self.last_encoded_bits)

        result_msg = (
            f"Physical Waveform Decoding Result:\n\n"
            f"Scheme Analyzed       : {self.current_scheme}\n"
            f"Transmitted Bitstream : {self.last_encoded_bits}\n"
            f"Decoded from Waveform : {decoded}\n\n"
            f"Verification Status   : {'SUCCESS (100% Exact Match)' if is_match else 'MISMATCH'}"
        )
        if is_match:
            messagebox.showinfo("Waveform Decoding (Extra Credit)", result_msg)
            self.lbl_status.config(text=f"Decoded: {decoded} (MATCH: 100%)", fg="#2f855a")
        else:
            messagebox.showwarning("Waveform Decoding Result", result_msg)
            self.lbl_status.config(text=f"Decoded: {decoded} (MISMATCH)", fg="#c53030")

    def on_modulate_analog(self):
        try:
            freq = float(self.entry_freq.get().strip() or "2.0")
            fs = int(self.entry_fs.get().strip() or "24")
        except ValueError:
            messagebox.showerror("Invalid Input", "Frequency and Sampling rate must be valid numbers.")
            return

        t_cont, a_cont, t_samp, samples = generate_analog_signal(freq=freq, duration=1.0, sampling_rate=fs)
        mod_type = self.var_mod.get()

        if mod_type == "PCM":
            try:
                num_bits = int(self.entry_pcm_bits.get().strip() or "3")
            except ValueError:
                num_bits = 3
            bitstream, q_vals, v_min, v_max = pcm_encode(samples, num_bits=num_bits)
            staircase = pcm_decode(bitstream, num_bits=num_bits, min_val=v_min, max_val=v_max)
            title = f"PCM ({num_bits}-bit) Staircase Reconstruction"
        else:
            try:
                step_size = float(self.entry_dm_step.get().strip() or "0.25")
            except ValueError:
                step_size = 0.25
            bitstream, staircase_enc = dm_encode(samples, step_size=step_size)
            staircase = dm_decode(bitstream, step_size=step_size)
            title = "Delta Modulation (DM) Staircase Reconstruction"

        self.last_modulated_stream = bitstream
        self.txt_mod_bits.delete("1.0", tk.END)
        self.txt_mod_bits.insert(tk.END, bitstream)

        # Render plot on analog canvas
        self.fig_analog.clear()
        ax = self.fig_analog.add_subplot(111)
        ax.plot(t_cont, a_cont, color="#1f77b4", linewidth=2.0, label="Continuous Analog Input", alpha=0.85)
        ax.scatter(t_samp, samples, color="#d62728", s=30, zorder=5, label="Discrete Samples")
        ax.step(t_samp, staircase, where="post", color="#ff7f0e", linewidth=2.2, label="Reconstructed Staircase")

        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.set_xlabel("Time (seconds)", fontsize=10, fontweight="bold")
        ax.set_ylabel("Amplitude (Volts)", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper right", framealpha=0.9)

        self.fig_analog.tight_layout()
        self.canvas_analog.draw()

    def on_feed_to_line_coding(self):
        bits = getattr(self, "last_modulated_stream", "").strip()
        if not bits:
            messagebox.showinfo("No Stream", "Please run Analog Modulation first.")
            return

        # Feed first 24 bits into Digital Tab
        sub_bits = bits[:24] if len(bits) > 24 else bits
        self._set_bits(sub_bits)
        self.notebook.select(self.tab_digital)
        self.on_encode_digital()
        messagebox.showinfo("Transferred", f"Fed {len(sub_bits)} bits of modulated data to Line Coding Tab!")


def launch_gui_window():
    app = SignalVisualizerGUI()
    app.mainloop()


# ^^^^^^^^ Test ke liye likha hai maine (START) ^^^^^^^^
# (Yeh section sirf is file ko akele chala kar check karne ke liye hai, main project logic upar hai)
if __name__ == "__main__":
    launch_gui_window()
# ^^^^^^^^ Test ke liye likha hai maine (END) ^^^^^^^^
