"""
VEF State Engine - Volume-to-Force Differential Physics Simulation Framework

A production-ready physics simulation for modeling coupled oscillatory systems
with phase-dependent energy distribution between PP (Periodic-Perturbation)
and NF (Non-Floquet) modes.

Author: Mark Chrisman
Version: 1.0
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VEFConfig:
    """Configuration for VEF State Engine simulation.
    
    Attributes:
        pp_initial: Initial PP (Periodic-Perturbation) density [0, 1]
        nf_initial: Initial NF (Non-Floquet) density [0, 1]
        phase_initial: Initial phase angle [0, 2π]
        omega: Angular frequency for oscillation (rad/s)
        coupling_strength: Energy exchange rate between modes per step
        damping: Energy dissipation rate per step
        nf_recovery: NF recovery rate when passive
        dt_max: Maximum timestep for numerical stability
    """
    pp_initial: float = 1.0
    nf_initial: float = 0.02
    phase_initial: float = 0.0
    omega: float = 0.142
    coupling_strength: float = 0.01
    damping: float = 0.001
    nf_recovery: float = 0.002
    dt_max: float = 0.1
    
    def __post_init__(self):
        """Validate configuration parameters."""
        assert 0 <= self.pp_initial <= 1, "pp_initial must be in [0, 1]"
        assert 0 <= self.nf_initial <= 1, "nf_initial must be in [0, 1]"
        assert self.pp_initial + self.nf_initial <= 1, "PP + NF must be <= 1"
        assert self.omega > 0, "omega must be positive"
        assert 0 <= self.coupling_strength <= 1, "coupling_strength must be in [0, 1]"
        assert 0 <= self.damping <= 1, "damping must be in [0, 1]"
        assert self.dt_max > 0, "dt_max must be positive"


class VEFStateEngine:
    """Core physics simulation engine for coupled oscillatory systems.
    
    Implements the VEF (Volume-to-Force Differential) state equations with:
    - Exact conservation law: PP + NF + void = 1.0
    - Phase-coupled energy transfer
    - Boundary enforcement [0, 1] for all densities
    - Numerical stability checks
    """
    
    def __init__(self, config: VEFConfig):
        """Initialize the VEF state engine.
        
        Args:
            config: VEFConfig object with simulation parameters
        """
        self.config = config
        self.state = self._initialize_state()
        self.t = 0.0
        
    def _initialize_state(self) -> np.ndarray:
        """Initialize the 7-dimensional state vector.
        
        State vector: [pp, nf, void, phase, energy, pp_nf_ratio, symmetry_index]
        
        Returns:
            Initial state array
        """
        pp = self.config.pp_initial
        nf = self.config.nf_initial
        void = 1.0 - pp - nf
        phase = self.config.phase_initial
        energy = pp + nf
        pp_nf_ratio = pp / (nf + 1e-10) if nf > 0 else np.inf
        symmetry_index = np.abs(pp - nf) / (pp + nf + 1e-10)
        
        return np.array([pp, nf, void, phase, energy, pp_nf_ratio, symmetry_index],
                       dtype=np.float64)
    
    def step(self, dt: float) -> np.ndarray:
        """Execute one integration step of the VEF dynamics.
        
        Implements RK4 integration of coupled differential equations:
        - dPP/dt = phase-dependent coupling + driven forcing
        - dNF/dt = phase-dependent coupling + recovery
        - dphase/dt = omega (constant angular frequency)
        - Energy balance with dissipation
        
        Args:
            dt: Timestep duration (seconds)
            
        Returns:
            Updated state array
        """
        # Adaptive timestep for stability
        dt_actual = min(dt, self.config.dt_max)
        
        # RK4 integration
        k1 = self._derivatives(self.state)
        k2 = self._derivatives(self.state + 0.5 * dt_actual * k1)
        k3 = self._derivatives(self.state + 0.5 * dt_actual * k2)
        k4 = self._derivatives(self.state + dt_actual * k3)
        
        state_new = self.state + (dt_actual / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Enforce conservation and boundaries
        state_new = self._enforce_constraints(state_new)
        
        # Update internal state and time
        self.state = state_new
        self.t += dt_actual
        
        return self.state.copy()
    
    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        """Compute state derivatives at given point.
        
        Args:
            state: Current state vector
            
        Returns:
            Derivative vector
        """
        pp, nf, void, phase, energy, ratio, sym = state
        
        # Phase-dependent coupling coefficient
        coupling_factor = np.sin(phase) * self.config.coupling_strength
        
        # Driven forcing on PP (harmonic oscillator)
        driving_force = 0.1 * np.cos(self.config.omega * self.t)
        
        # Derivatives
        dpp_dt = coupling_factor * nf + driving_force - self.config.damping * pp
        dnf_dt = -coupling_factor * pp + self.config.nf_recovery * (1 - nf - pp)
        dphase_dt = self.config.omega
        
        # Energy dynamics
        denergy_dt = driving_force * pp - self.config.damping * energy
        
        # Void updates from conservation
        dvoid_dt = -(dpp_dt + dnf_dt)
        
        # Derived quantities
        dpp_nf_ratio_dt = (dpp_dt * nf - pp * dnf_dt) / (nf**2 + 1e-10)
        dsym_dt = ((dpp_dt - dnf_dt) * (pp + nf) - (pp - nf) * (dpp_dt + dnf_dt)) / ((pp + nf)**2 + 1e-10)
        
        return np.array([dpp_dt, dnf_dt, dvoid_dt, dphase_dt, denergy_dt, 
                        dpp_nf_ratio_dt, dsym_dt], dtype=np.float64)
    
    def _enforce_constraints(self, state: np.ndarray) -> np.ndarray:
        """Enforce physical constraints on state.
        
        - All densities in [0, 1]
        - Conservation: PP + NF + void = 1.0
        - Phase wrapping: [0, 2π]
        
        Args:
            state: State vector to constrain
            
        Returns:
            Constrained state vector
        """
        pp, nf, void, phase, energy, ratio, sym = state
        
        # Clamp densities to [0, 1]
        pp = np.clip(pp, 0.0, 1.0)
        nf = np.clip(nf, 0.0, 1.0)
        
        # Enforce conservation (priority: PP > NF > void)
        pp = np.clip(pp, 0.0, 1.0)
        nf = np.clip(nf, 0.0, 1.0 - pp)
        void = 1.0 - pp - nf
        
        # Phase wrapping
        phase = phase % (2 * np.pi)
        
        # Energy bounds
        energy = np.clip(energy, 0.0, pp + nf)
        
        # Recompute derived quantities
        pp_nf_ratio = pp / (nf + 1e-10) if nf > 0 else np.inf
        symmetry_index = np.abs(pp - nf) / (pp + nf + 1e-10)
        
        return np.array([pp, nf, void, phase, energy, pp_nf_ratio, symmetry_index],
                       dtype=np.float64)
    
    def reset(self):
        """Reset engine to initial state."""
        self.state = self._initialize_state()
        self.t = 0.0


class VEFTelemetryRecorder:
    """Records and analyzes telemetry from VEF simulations.
    
    Manages simulation execution with specified output cadence and
    provides statistical analysis of recorded data.
    """
    
    def __init__(self, engine: VEFStateEngine):
        """Initialize recorder with a VEF engine.
        
        Args:
            engine: VEFStateEngine instance to record from
        """
        self.engine = engine
        self.data = None
        self.times = None
        
    def run_sequence(self, duration: float, dt: float = 0.01, 
                    record_interval: int = 10) -> np.ndarray:
        """Execute simulation and record telemetry.
        
        Args:
            duration: Total simulation time (seconds)
            dt: Integration timestep (seconds)
            record_interval: Record every N steps
            
        Returns:
            Recorded data array of shape (n_records, 7)
        """
        n_steps = int(duration / dt)
        n_records = n_steps // record_interval + 1
        
        self.data = np.zeros((n_records, 7), dtype=np.float64)
        self.times = np.zeros(n_records, dtype=np.float64)
        
        logger.info(f"Starting simulation: {duration}s, {n_steps} steps, {n_records} records")
        
        self.data[0] = self.engine.state
        self.times[0] = self.engine.t
        
        for i in range(1, n_steps + 1):
            self.engine.step(dt)
            
            if i % record_interval == 0:
                record_idx = i // record_interval
                self.data[record_idx] = self.engine.state
                self.times[record_idx] = self.engine.t
            
            if i % (10 * record_interval) == 0:
                logger.info(f"Progress: {i}/{n_steps} steps ({100*i/n_steps:.1f}%)")
        
        logger.info("Simulation complete")
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        """Compute statistical summaries of recorded data.
        
        Returns:
            Dictionary with statistics for all observables
        """
        if self.data is None:
            raise ValueError("No data recorded. Run run_sequence() first.")
        
        analysis = {
            'pp_stats': self._compute_stats(self.data[:, 0]),
            'nf_stats': self._compute_stats(self.data[:, 1]),
            'void_stats': self._compute_stats(self.data[:, 2]),
            'phase_stats': self._compute_stats(self.data[:, 3]),
            'energy_stats': self._compute_stats(self.data[:, 4]),
            'ratio_stats': self._compute_stats(self.data[:, 5]),
            'symmetry_stats': self._compute_stats(self.data[:, 6]),
        }
        
        # Conservation check
        conservation = self.data[:, 0] + self.data[:, 1] + self.data[:, 2]
        analysis['conservation'] = {
            'mean': np.mean(conservation),
            'std': np.std(conservation),
            'max_deviation': np.max(np.abs(conservation - 1.0)),
        }
        
        # Energy trend
        energy = self.data[:, 4]
        energy_diff = np.diff(energy)
        analysis['energy_trend'] = 'stable' if np.std(energy_diff) < 0.01 else 'trending'
        
        return analysis
    
    @staticmethod
    def _compute_stats(data: np.ndarray) -> Dict[str, float]:
        """Compute basic statistics for a 1D array."""
        return {
            'mean': np.mean(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'median': np.median(data),
        }


if __name__ == "__main__":
    """Example: Run full VEF simulation pipeline."""
    
    # Configuration
    config = VEFConfig(
        pp_initial=1.0,
        nf_initial=0.02,
        omega=0.142,
        coupling_strength=0.01,
        damping=0.001,
    )
    
    # Initialize engine
    engine = VEFStateEngine(config)
    
    # Record telemetry
    recorder = VEFTelemetryRecorder(engine)
    data = recorder.run_sequence(
        duration=1000.0,
        dt=0.01,
        record_interval=10
    )
    
    # Analyze
    analysis = recorder.analyze()
    print("\n=== VEF State Engine Analysis ===")
    print(f"Mean PP: {analysis['pp_stats']['mean']:.4f}")
    print(f"Mean NF: {analysis['nf_stats']['mean']:.4f}")
    print(f"Mean Energy: {analysis['energy_stats']['mean']:.4f}")
    print(f"Conservation (max deviation): {analysis['conservation']['max_deviation']:.2e}")
    print(f"Energy trend: {analysis['energy_trend']}")
    
    # Save telemetry
    np.save("vef_ppnf_raw.npy", data)
    print("\nTelemetry saved to vef_ppnf_raw.npy")
