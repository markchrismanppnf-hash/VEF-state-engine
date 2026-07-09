"""
VEF Visualization Module - Comprehensive analysis and plotting tools

Provides multiple visualization types for VEF state engine data:
- Phase portraits with phase-color encoding
- Time series of all state variables
- Energy dynamics analysis
- Symmetry and phase alignment quality
- Comparison against reference models
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import logging
from typing import Tuple, Optional, Dict, List

logger = logging.getLogger(__name__)


class VEFVisualizer:
    """Comprehensive visualization toolkit for VEF data."""
    
    FIGSIZE_DEFAULT = (14, 10)
    DPI = 100
    
    def __init__(self, figsize: Tuple[int, int] = FIGSIZE_DEFAULT, dpi: int = DPI):
        """Initialize visualizer with figure settings.
        
        Args:
            figsize: Default figure size (width, height)
            dpi: Resolution in dots per inch
        """
        self.figsize = figsize
        self.dpi = dpi
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_phase_portrait(self, data: np.ndarray, 
                           title: str = "VEF Phase Portrait: PP vs NF") -> plt.Figure:
        """Create phase portrait with phase-dependent coloring.
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            title: Figure title
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        pp = data[:, 0]
        nf = data[:, 1]
        phase = data[:, 3]
        
        # Create scatter plot colored by phase
        norm = Normalize(vmin=0, vmax=2*np.pi)
        cmap = plt.cm.hsv
        scatter = ax.scatter(pp, nf, c=phase, cmap=cmap, norm=norm, 
                            s=20, alpha=0.6, edgecolors='none')
        
        # Add conservation boundary
        pp_boundary = np.linspace(0, 1, 100)
        nf_boundary = 1.0 - pp_boundary
        ax.plot(pp_boundary, nf_boundary, 'k--', linewidth=2, 
               label='Conservation boundary: PP+NF=1', alpha=0.5)
        
        ax.set_xlabel('PP Density', fontsize=12, fontweight='bold')
        ax.set_ylabel('NF Density', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        
        # Colorbar for phase
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Phase (radians)', fontsize=11, fontweight='bold')
        
        ax.legend(loc='upper right', fontsize=10)
        plt.tight_layout()
        
        return fig
    
    def plot_time_series(self, data: np.ndarray, times: Optional[np.ndarray] = None,
                        title: str = "VEF Time Series") -> plt.Figure:
        """Plot all state variables over time.
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            times: Time points for x-axis (auto-generated if None)
            title: Figure title
            
        Returns:
            Matplotlib figure object
        """
        if times is None:
            times = np.linspace(0, 1000, len(data))
        
        fig, axes = plt.subplots(3, 2, figsize=self.figsize, dpi=self.dpi)
        
        # PP density
        axes[0, 0].plot(times, data[:, 0], 'b-', linewidth=1.5, label='PP')
        axes[0, 0].set_ylabel('PP Density', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_ylim([0, 1.05])
        
        # NF density
        axes[0, 1].plot(times, data[:, 1], 'r-', linewidth=1.5, label='NF')
        axes[0, 1].set_ylabel('NF Density', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_ylim([0, 1.05])
        
        # Void fraction
        axes[1, 0].plot(times, data[:, 2], 'g-', linewidth=1.5, label='Void')
        axes[1, 0].set_ylabel('Void Fraction', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim([0, 1.05])
        
        # Phase
        axes[1, 1].plot(times, data[:, 3], 'purple', linewidth=1.5, label='Phase')
        axes[1, 1].set_ylabel('Phase (rad)', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Energy
        axes[2, 0].plot(times, data[:, 4], 'orange', linewidth=1.5, label='Energy')
        axes[2, 0].set_ylabel('Energy', fontweight='bold')
        axes[2, 0].set_xlabel('Time (s)', fontweight='bold')
        axes[2, 0].grid(True, alpha=0.3)
        
        # PP/NF ratio (log scale)
        ratio = data[:, 5]
        ratio = np.clip(ratio, 0.01, 1000)  # Clip for visualization
        axes[2, 1].semilogy(times, ratio, 'brown', linewidth=1.5, label='PP/NF Ratio')
        axes[2, 1].set_ylabel('Ratio (log scale)', fontweight='bold')
        axes[2, 1].set_xlabel('Time (s)', fontweight='bold')
        axes[2, 1].grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return fig
    
    def plot_energy_analysis(self, data: np.ndarray, 
                            times: Optional[np.ndarray] = None,
                            title: str = "VEF Energy Dynamics") -> plt.Figure:
        """Comprehensive energy analysis with multiple perspectives.
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            times: Time points for x-axis (auto-generated if None)
            title: Figure title
            
        Returns:
            Matplotlib figure object
        """
        if times is None:
            times = np.linspace(0, 1000, len(data))
        
        fig, axes = plt.subplots(2, 2, figsize=self.figsize, dpi=self.dpi)
        
        energy = data[:, 4]
        pp = data[:, 0]
        nf = data[:, 1]
        
        # Total energy time series
        axes[0, 0].plot(times, energy, 'k-', linewidth=2)
        axes[0, 0].fill_between(times, energy, alpha=0.3)
        axes[0, 0].set_ylabel('Total Energy', fontweight='bold')
        axes[0, 0].set_title('Energy Evolution', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Energy histogram (PDF)
        axes[0, 1].hist(energy, bins=50, density=True, color='skyblue', 
                       edgecolor='black', alpha=0.7)
        axes[0, 1].set_xlabel('Energy Value', fontweight='bold')
        axes[0, 1].set_ylabel('Probability Density', fontweight='bold')
        axes[0, 1].set_title('Energy Distribution', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Mode energy breakdown
        pp_energy = pp * energy / (pp + nf + 1e-10)
        nf_energy = nf * energy / (pp + nf + 1e-10)
        axes[1, 0].plot(times, pp_energy, 'b-', linewidth=1.5, label='PP Energy')
        axes[1, 0].plot(times, nf_energy, 'r-', linewidth=1.5, label='NF Energy')
        axes[1, 0].set_ylabel('Mode Energy', fontweight='bold')
        axes[1, 0].set_xlabel('Time (s)', fontweight='bold')
        axes[1, 0].set_title('Mode Energy Breakdown', fontweight='bold')
        axes[1, 0].legend(loc='best', fontsize=10)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Energy rate of change
        denergy_dt = np.diff(energy) / np.diff(times)
        axes[1, 1].plot(times[:-1], denergy_dt, 'purple', linewidth=1.5)
        axes[1, 1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axes[1, 1].set_ylabel('dE/dt', fontweight='bold')
        axes[1, 1].set_xlabel('Time (s)', fontweight='bold')
        axes[1, 1].set_title('Energy Rate of Change', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return fig
    
    def plot_symmetry_analysis(self, data: np.ndarray,
                              times: Optional[np.ndarray] = None,
                              title: str = "VEF Symmetry Analysis") -> plt.Figure:
        """Analyze phase alignment and symmetry quality.
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            times: Time points for x-axis (auto-generated if None)
            title: Figure title
            
        Returns:
            Matplotlib figure object
        """
        if times is None:
            times = np.linspace(0, 1000, len(data))
        
        fig, axes = plt.subplots(2, 2, figsize=self.figsize, dpi=self.dpi)
        
        pp = data[:, 0]
        nf = data[:, 1]
        phase = data[:, 3]
        symmetry = data[:, 6]
        
        # Symmetry index over time
        axes[0, 0].plot(times, symmetry, 'g-', linewidth=2)
        axes[0, 0].fill_between(times, symmetry, alpha=0.3, color='green')
        axes[0, 0].set_ylabel('Symmetry Index', fontweight='bold')
        axes[0, 0].set_title('Phase Alignment Quality', fontweight='bold')
        axes[0, 0].set_ylim([0, 1])
        axes[0, 0].grid(True, alpha=0.3)
        
        # Phase vs symmetry scatter
        norm = Normalize(vmin=np.min(symmetry), vmax=np.max(symmetry))
        scatter = axes[0, 1].scatter(phase, symmetry, c=symmetry, cmap='RdYlGn_r',
                                    norm=norm, s=30, alpha=0.6)
        axes[0, 1].set_xlabel('Phase (rad)', fontweight='bold')
        axes[0, 1].set_ylabel('Symmetry Index', fontweight='bold')
        axes[0, 1].set_title('Phase-Symmetry Coupling', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=axes[0, 1])
        cbar.set_label('Symmetry', fontsize=10)
        
        # PP-NF difference evolution
        pp_nf_diff = pp - nf
        axes[1, 0].plot(times, pp_nf_diff, 'purple', linewidth=1.5)
        axes[1, 0].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axes[1, 0].fill_between(times, pp_nf_diff, alpha=0.3, color='purple')
        axes[1, 0].set_ylabel('PP - NF', fontweight='bold')
        axes[1, 0].set_xlabel('Time (s)', fontweight='bold')
        axes[1, 0].set_title('Density Difference Evolution', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Symmetry distribution
        axes[1, 1].hist(symmetry, bins=40, density=True, color='orange',
                       edgecolor='black', alpha=0.7)
        axes[1, 1].set_xlabel('Symmetry Index', fontweight='bold')
        axes[1, 1].set_ylabel('Probability Density', fontweight='bold')
        axes[1, 1].set_title('Symmetry Distribution', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return fig
    
    def plot_comparison(self, data_main: np.ndarray, data_ref: np.ndarray,
                       times: Optional[np.ndarray] = None,
                       labels: Tuple[str, str] = ("VEF Model", "Reference"),
                       title: str = "VEF Model Comparison") -> plt.Figure:
        """Compare VEF model against reference dataset.
        
        Args:
            data_main: Main VEF telemetry data
            data_ref: Reference data for comparison
            times: Time points for x-axis
            labels: Labels for main and reference data
            title: Figure title
            
        Returns:
            Matplotlib figure object
        """
        if times is None:
            times = np.linspace(0, 1000, len(data_main))
        
        # Align lengths
        min_len = min(len(data_main), len(data_ref))
        data_main = data_main[:min_len]
        data_ref = data_ref[:min_len]
        times = times[:min_len]
        
        fig, axes = plt.subplots(2, 2, figsize=self.figsize, dpi=self.dpi)
        
        # PP comparison
        axes[0, 0].plot(times, data_main[:, 0], 'b-', linewidth=2, label=labels[0])
        axes[0, 0].plot(times, data_ref[:, 0], 'b--', linewidth=1.5, 
                       label=labels[1], alpha=0.7)
        axes[0, 0].set_ylabel('PP Density', fontweight='bold')
        axes[0, 0].set_title('PP Mode Comparison', fontweight='bold')
        axes[0, 0].legend(loc='best', fontsize=10)
        axes[0, 0].grid(True, alpha=0.3)
        
        # NF comparison
        axes[0, 1].plot(times, data_main[:, 1], 'r-', linewidth=2, label=labels[0])
        axes[0, 1].plot(times, data_ref[:, 1], 'r--', linewidth=1.5,
                       label=labels[1], alpha=0.7)
        axes[0, 1].set_ylabel('NF Density', fontweight='bold')
        axes[0, 1].set_title('NF Mode Comparison', fontweight='bold')
        axes[0, 1].legend(loc='best', fontsize=10)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Energy comparison
        axes[1, 0].plot(times, data_main[:, 4], 'orange', linewidth=2, label=labels[0])
        axes[1, 0].plot(times, data_ref[:, 4], 'orange', linewidth=1.5, 
                       linestyle='--', label=labels[1], alpha=0.7)
        axes[1, 0].set_ylabel('Energy', fontweight='bold')
        axes[1, 0].set_xlabel('Time (s)', fontweight='bold')
        axes[1, 0].set_title('Energy Comparison', fontweight='bold')
        axes[1, 0].legend(loc='best', fontsize=10)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Residuals
        residual_pp = np.abs(data_main[:, 0] - data_ref[:, 0])
        residual_nf = np.abs(data_main[:, 1] - data_ref[:, 1])
        residual_energy = np.abs(data_main[:, 4] - data_ref[:, 4])
        
        axes[1, 1].semilogy(times, residual_pp, 'b-', linewidth=1.5, label='PP Residual')
        axes[1, 1].semilogy(times, residual_nf, 'r-', linewidth=1.5, label='NF Residual')
        axes[1, 1].semilogy(times, residual_energy, 'orange', linewidth=1.5, 
                           label='Energy Residual')
        axes[1, 1].set_ylabel('Absolute Difference (log)', fontweight='bold')
        axes[1, 1].set_xlabel('Time (s)', fontweight='bold')
        axes[1, 1].set_title('Model Residuals', fontweight='bold')
        axes[1, 1].legend(loc='best', fontsize=9)
        axes[1, 1].grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return fig


def create_all_visualizations(data_path: str = "vef_ppnf_raw.npy",
                              output_dir: str = ".") -> Dict[str, str]:
    """Generate all standard VEF visualizations.
    
    Args:
        data_path: Path to saved telemetry data
        output_dir: Directory for output PNG files
        
    Returns:
        Dictionary mapping plot names to output file paths
    """
    logger.info(f"Loading data from {data_path}")
    data = np.load(data_path)
    
    viz = VEFVisualizer()
    outputs = {}
    
    # Phase portrait
    fig = viz.plot_phase_portrait(data)
    output_file = f"{output_dir}/vef_analysis_phase_portrait.png"
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    outputs['phase_portrait'] = output_file
    logger.info(f"Saved: {output_file}")
    plt.close(fig)
    
    # Time series
    fig = viz.plot_time_series(data)
    output_file = f"{output_dir}/vef_analysis_time_series.png"
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    outputs['time_series'] = output_file
    logger.info(f"Saved: {output_file}")
    plt.close(fig)
    
    # Energy analysis
    fig = viz.plot_energy_analysis(data)
    output_file = f"{output_dir}/vef_analysis_energy.png"
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    outputs['energy'] = output_file
    logger.info(f"Saved: {output_file}")
    plt.close(fig)
    
    # Symmetry analysis
    fig = viz.plot_symmetry_analysis(data)
    output_file = f"{output_dir}/vef_analysis_symmetry.png"
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    outputs['symmetry'] = output_file
    logger.info(f"Saved: {output_file}")
    plt.close(fig)
    
    return outputs


if __name__ == "__main__":
    """Generate all visualizations."""
    outputs = create_all_visualizations()
    print("\n=== Visualizations Generated ===")
    for name, path in outputs.items():
        print(f"  {name}: {path}")
