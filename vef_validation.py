"""
VEF Validation Module - Testing and verification framework

Comprehensive validation suite for VEF simulations:
- Conservation law verification (PP + NF + void = 1.0)
- Boundary condition enforcement [0, 1]
- Energy smoothness and monotonicity
- Phase continuity
- Parameter sweep validation
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import logging

from vef_state_engine_improved import VEFStateEngine, VEFConfig, VEFTelemetryRecorder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class VEFValidator:
    """Validation framework for VEF simulations."""
    
    CONSERVATION_TOLERANCE = 1e-10
    BOUNDARY_TOLERANCE = 1e-6
    ENERGY_SMOOTHNESS_TOLERANCE = 0.025
    
    @staticmethod
    def check_conservation(data: np.ndarray, tolerance: float = CONSERVATION_TOLERANCE) -> Dict[str, Any]:
        """Verify PP + NF + void = 1.0 conservation law.
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            tolerance: Maximum allowed deviation from 1.0
            
        Returns:
            Validation result dictionary
        """
        densities_sum = data[:, 0] + data[:, 1] + data[:, 2]
        deviations = np.abs(densities_sum - 1.0)
        max_dev = np.max(deviations)
        mean_dev = np.mean(deviations)
        
        passed = max_dev < tolerance
        
        return {
            'passed': passed,
            'max_deviation': max_dev,
            'mean_deviation': mean_dev,
            'tolerance': tolerance,
            'message': f"{'✓' if passed else '✗'} Conservation: max dev = {max_dev:.2e}"
        }
    
    @staticmethod
    def check_bounds(data: np.ndarray, tolerance: float = BOUNDARY_TOLERANCE) -> Dict[str, Any]:
        """Verify all densities are in [0, 1].
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            tolerance: Small tolerance for numerical errors
            
        Returns:
            Validation result dictionary
        """
        pp = data[:, 0]
        nf = data[:, 1]
        void = data[:, 2]
        
        violations = []
        
        if np.min(pp) < -tolerance or np.max(pp) > 1 + tolerance:
            violations.append(f"PP out of bounds: [{np.min(pp):.6f}, {np.max(pp):.6f}]")
        
        if np.min(nf) < -tolerance or np.max(nf) > 1 + tolerance:
            violations.append(f"NF out of bounds: [{np.min(nf):.6f}, {np.max(nf):.6f}]")
        
        if np.min(void) < -tolerance or np.max(void) > 1 + tolerance:
            violations.append(f"Void out of bounds: [{np.min(void):.6f}, {np.max(void):.6f}]")
        
        passed = len(violations) == 0
        
        return {
            'passed': passed,
            'violations': violations,
            'message': f"{'✓' if passed else '✗'} Boundary conditions: {len(violations)} violations"
        }
    
    @staticmethod
    def check_energy_smoothness(data: np.ndarray, 
                               tolerance: float = ENERGY_SMOOTHNESS_TOLERANCE) -> Dict[str, Any]:
        """Verify energy changes are smooth (no large jumps).
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            tolerance: Maximum allowed step size
            
        Returns:
            Validation result dictionary
        """
        energy = data[:, 4]
        energy_diff = np.abs(np.diff(energy))
        max_step = np.max(energy_diff)
        mean_step = np.mean(energy_diff)
        
        passed = max_step < tolerance
        
        return {
            'passed': passed,
            'max_step': max_step,
            'mean_step': mean_step,
            'tolerance': tolerance,
            'message': f"{'✓' if passed else '✗'} Energy smoothness: max step = {max_step:.6f}"
        }
    
    @staticmethod
    def check_phase_continuity(data: np.ndarray) -> Dict[str, Any]:
        """Verify phase progression is continuous and monotonic (mod 2π).
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            
        Returns:
            Validation result dictionary
        """
        phase = data[:, 3]
        phase_unwrapped = np.unwrap(phase)
        phase_diff = np.diff(phase_unwrapped)
        
        # Check for monotonicity (should always increase)
        monotonic = np.all(phase_diff >= 0)
        
        # Check for large jumps (wrapped phase)
        wrapped_jumps = np.sum(np.abs(phase_diff) > np.pi)
        
        passed = monotonic
        
        return {
            'passed': passed,
            'monotonic': monotonic,
            'wrapped_jumps': int(wrapped_jumps),
            'message': f"{'✓' if passed else '✗'} Phase continuity: monotonic={monotonic}, jumps={wrapped_jumps}"
        }
    
    @staticmethod
    def check_energy_trend(data: np.ndarray) -> Dict[str, Any]:
        """Analyze energy trend (stable, decaying, or growing).
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            
        Returns:
            Trend classification and statistics
        """
        energy = data[:, 4]
        
        # Split into quarters and compare mean energy
        q1_mean = np.mean(energy[:len(energy)//4])
        q4_mean = np.mean(energy[3*len(energy)//4:])
        
        change_rate = (q4_mean - q1_mean) / (q1_mean + 1e-10)
        
        if abs(change_rate) < 0.05:
            trend = 'stable'
        elif change_rate < -0.05:
            trend = 'decaying'
        else:
            trend = 'growing'
        
        return {
            'trend': trend,
            'q1_mean': q1_mean,
            'q4_mean': q4_mean,
            'change_rate': change_rate,
            'message': f"Energy trend: {trend} (change rate: {change_rate:+.2%})"
        }
    
    @classmethod
    def validate_all(cls, data: np.ndarray) -> Dict[str, Dict]:
        """Run all validation checks on data.
        
        Args:
            data: Telemetry data of shape (n_records, 7)
            
        Returns:
            Dictionary with all validation results
        """
        results = {
            'conservation': cls.check_conservation(data),
            'bounds': cls.check_bounds(data),
            'energy_smoothness': cls.check_energy_smoothness(data),
            'phase_continuity': cls.check_phase_continuity(data),
            'energy_trend': cls.check_energy_trend(data),
        }
        
        return results
    
    @staticmethod
    def print_validation_report(results: Dict[str, Dict]):
        """Print formatted validation report.
        
        Args:
            results: Dictionary from validate_all()
        """
        print("\n" + "="*60)
        print("VEF VALIDATION REPORT")
        print("="*60)
        
        all_passed = True
        for check_name, check_result in results.items():
            if check_name == 'energy_trend':
                print(f"\n{check_result['message']}")
            else:
                passed = check_result.get('passed', None)
                message = check_result.get('message', '')
                print(f"\n{message}")
                if passed is not None and not passed:
                    all_passed = False
                    if 'violations' in check_result and check_result['violations']:
                        for violation in check_result['violations']:
                            print(f"  → {violation}")
        
        print("\n" + "="*60)
        status = "✓ ALL CHECKS PASSED" if all_passed else "✗ SOME CHECKS FAILED"
        print(status)
        print("="*60 + "\n")


def run_parameter_sweep() -> Dict[str, List[Dict]]:
    """Run validation across parameter sweep configurations.
    
    Tests 27 parameter combinations:
    - coupling_strength ∈ {0.005, 0.01, 0.02}
    - damping ∈ {0.0005, 0.001, 0.002}
    - omega ∈ {0.1, 0.142, 0.2}
    
    Returns:
        Dictionary mapping config strings to validation results
    """
    coupling_vals = [0.005, 0.01, 0.02]
    damping_vals = [0.0005, 0.001, 0.002]
    omega_vals = [0.1, 0.142, 0.2]
    
    results = {}
    config_count = 0
    passed_count = 0
    
    print("\nRunning parameter sweep (27 configurations)...")
    print("-" * 60)
    
    for omega in omega_vals:
        for coupling in coupling_vals:
            for damping in damping_vals:
                config_count += 1
                config_key = f"ω={omega:.3f}_c={coupling:.3f}_d={damping:.4f}"
                
                try:
                    # Run simulation
                    config = VEFConfig(
                        pp_initial=1.0,
                        nf_initial=0.02,
                        omega=omega,
                        coupling_strength=coupling,
                        damping=damping,
                    )
                    engine = VEFStateEngine(config)
                    recorder = VEFTelemetryRecorder(engine)
                    data = recorder.run_sequence(duration=100.0, dt=0.01, record_interval=10)
                    
                    # Validate
                    val_results = VEFValidator.validate_all(data)
                    
                    # Check if all passed
                    all_passed = (
                        val_results['conservation']['passed'] and
                        val_results['bounds']['passed'] and
                        val_results['energy_smoothness']['passed'] and
                        val_results['phase_continuity']['passed']
                    )
                    
                    if all_passed:
                        passed_count += 1
                        status = "✓"
                    else:
                        status = "✗"
                    
                    results[config_key] = {
                        'validation': val_results,
                        'passed': all_passed,
                    }
                    
                    print(f"[{config_count:2d}/27] {status} {config_key}")
                    
                except Exception as e:
                    print(f"[{config_count:2d}/27] ✗ {config_key} - ERROR: {str(e)[:40]}")
                    results[config_key] = {'error': str(e), 'passed': False}
    
    print("-" * 60)
    print(f"\nParameter sweep complete: {passed_count}/{config_count} configurations passed")
    
    return results


if __name__ == "__main__":
    """Run full validation suite."""
    
    # First, load or generate test data
    print("VEF Validation Suite")
    print("=" * 60)
    
    try:
        # Try to load existing data
        data = np.load("vef_ppnf_raw.npy")
        print("Loaded existing telemetry data from vef_ppnf_raw.npy")
    except FileNotFoundError:
        # Generate new data
        print("Generating test data...")
        config = VEFConfig(
            pp_initial=1.0,
            nf_initial=0.02,
            omega=0.142,
            coupling_strength=0.01,
            damping=0.001,
        )
        engine = VEFStateEngine(config)
        recorder = VEFTelemetryRecorder(engine)
        data = recorder.run_sequence(duration=1000.0, dt=0.01, record_interval=10)
        np.save("vef_ppnf_raw.npy", data)
        print("Generated and saved test data to vef_ppnf_raw.npy")
    
    # Single configuration validation
    print("\n--- Single Configuration Validation ---")
    results = VEFValidator.validate_all(data)
    VEFValidator.print_validation_report(results)
    
    # Parameter sweep
    print("\n--- Parameter Sweep Validation ---")
    sweep_results = run_parameter_sweep()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    passed = sum(1 for r in sweep_results.values() if r.get('passed', False))
    total = len(sweep_results)
    print(f"Configurations passed: {passed}/{total}")
    print(f"Pass rate: {100*passed/total:.1f}%")
    
    if passed == total:
        print("\n✓ ALL CONFIGURATIONS VALID - FRAMEWORK IS PRODUCTION READY")
    else:
        print("\n✗ Some configurations failed - review errors above")
