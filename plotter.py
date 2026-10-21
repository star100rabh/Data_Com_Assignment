"""
plotter.py
Visual waveform plotter for line coding and digital signals.
Plots voltage levels over time with bit annotations and grid lines.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_line_code(bitstream: str, time: np.ndarray, voltage: np.ndarray, 
                   scheme_name: str, labels: list = None, save_path: str = None, show: bool = False):
    """
    Plots the digital waveform for a given line coding scheme.

    Parameters:
        bitstream (str): The original binary stream (e.g. '1011001').
        time (np.ndarray): Time axis points.
        voltage (np.ndarray): Corresponding voltage levels.
        scheme_name (str): Name of the line coding scheme (e.g. 'NRZ-L').
        labels (list, optional): Custom annotations for each bit interval (e.g. ['0', 'V', 'B']).
        save_path (str, optional): File path to save the plot image.
        show (bool): Whether to call plt.show() interactively.
    """
    num_bits = len(bitstream)
    display_labels = labels if labels is not None and len(labels) == num_bits else list(bitstream)
    
    fig, ax = plt.subplots(figsize=(max(10, num_bits * 0.8), 4))
    
    # Plot the voltage waveform
    ax.plot(time, voltage, color="#0066cc", linewidth=2.2, label=f"{scheme_name} Signal")
    
    # Draw reference zero line
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)
    
    # Draw vertical grid lines at each bit boundary and annotate bits
    for i, lbl in enumerate(display_labels):
        ax.axvline(i, color="lightgray", linestyle=":", linewidth=1)
        # Highlight violations (V) or balancing pulses (B) with distinct colors
        box_bg = "#eef5ff"
        box_border = "#99ccff"
        if "V" in str(lbl):
            box_bg = "#ffebee"
            box_border = "#ef5350"
        elif "B" in str(lbl):
            box_bg = "#e8f5e9"
            box_border = "#66bb6a"

        # Display the bit / symbol in the center of the bit duration
        ax.text(i + 0.5, 1.4, str(lbl), fontsize=11, fontweight="bold", 
                ha="center", va="center", color="#333333",
                bbox=dict(boxstyle="circle,pad=0.2", facecolor=box_bg, edgecolor=box_border))

    # Final boundary line
    ax.axvline(num_bits, color="lightgray", linestyle=":", linewidth=1)
    
    # Configure axes and limits
    ax.set_xlim(0, num_bits)
    ax.set_ylim(-1.8, 1.8)
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(["-V (-1)", "0 V", "+V (+1)"])
    ax.set_xticks(range(num_bits + 1))
    
    ax.set_xlabel("Bit Interval (Time)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Voltage Level", fontsize=11, fontweight="bold")
    ax.set_title(f"Line Coding Waveform: {scheme_name}", fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, which="both", axis="y", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"[Plot saved to: {save_path}]")
        
    if show:
        plt.show()
        
    plt.close(fig)


def plot_analog_and_staircase(t_analog: np.ndarray, signal_analog: np.ndarray, 
                              t_samples: np.ndarray, sample_values: np.ndarray, 
                              reconstructed_staircase: np.ndarray, 
                              title: str = "Modulation & Staircase Reconstruction", 
                              save_path: str = None, show: bool = False):
    """
    Plots the continuous analog signal along with discrete samples and the reconstructed
    staircase waveform produced by the decoder.
    """
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    # 1. Continuous analog signal
    ax.plot(t_analog, signal_analog, color="#1f77b4", linewidth=2.0, label="Original Analog Signal", alpha=0.85)
    
    # 2. Discrete samples
    ax.scatter(t_samples, sample_values, color="#d62728", s=35, zorder=5, label="Sampled Points")
    
    # 3. Staircase reconstructed signal
    ax.step(t_samples, reconstructed_staircase, where="post", color="#ff7f0e", 
            linewidth=2.2, label="Reconstructed Staircase Signal")
    
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_xlabel("Time (seconds)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Amplitude (Volts)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"[Plot saved to: {save_path}]")
    if show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    print("--- Waveform Plotter Self-Check ---")
    
    # Simple dummy rectangular signal test
    test_bits = "1010"
    t = np.linspace(0, 4, 400)
    # Alternate voltage +1 and -1 for 4 bits
    v = np.repeat([1, -1, 1, -1], 100)
    
    plot_line_code(test_bits, t, v, "Test Rectangular Wave", save_path="test_plot.png")
    print("Self-check completed: test_plot.png generated successfully.")

