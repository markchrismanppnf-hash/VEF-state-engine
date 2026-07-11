# Contributing to VEF State Engine

Thank you for your interest in contributing to the VEF State Engine project! This document provides guidelines and instructions for collaboration.

---

## 🎯 Philosophy & Design Principles

Before diving into code contributions, it's essential to understand the **core design philosophy** that makes VEF work:

### PP–NF Complementarity Model

VEF operates a **dual-density medium** with two fields: **PP (Periodic-Perturbation)** and **NF (Non-Floquet)**.

#### Core Rules (Non-Negotiable)

**Rule 1: PP is the active field. NF is always derived.**

```python
# ✓ CORRECT: NF is computed from PP after PP evolves
pp_new = evolve_pp_physics(pp_old)
nf_new = 1.0 - pp_new - void  # NF ALWAYS comes from PP

# ✗ WRONG: Evolving NF independently
nf_new = evolve_nf_independently(nf_old)  # Never do this!
```

**Rule 2: Conservation is a law, not a convenience.**

```python
# ✓ CORRECT: Conservation enforced everywhere
assert np.allclose(pp + nf + void, 1.0), "Conservation violated"

# ✗ WRONG: Conservation "approximately" maintained
if pp + nf + void > 0.99:  # Close enough?
    pass
```

**Rule 3: NF has no independent dynamics.**

```python
# ✓ CORRECT: All physics happens on PP
dpp_dt = coupling * sin(phase) - damping * pp
dnf_dt = -(dpp_dt + dvoid_dt)  # NF changes only because PP changed

# ✗ WRONG: Adding separate NF physics
dnf_dt = recovery_term + additional_nf_process  # NF isn't independent!
```

**Rule 4: The interface is primary.**

The PP–NF interface (where they meet) is where geometry lives. All curvature, boundary structure, and interface forces originate here. Future physics modules must treat the interface as the primary geometric object, not an afterthought.

**Rule 5: All extensions follow the same pattern.**

When adding new physics modules (lag, EOS, radiation, shells, coupling energy), they must:
1. Operate **only on PP**
2. Respect **PP + NF + void = 1.0** always
3. Recompute **NF from PP** after evolution
4. Maintain **determinism** (no stochastic behavior unless explicitly added)

#### Examples of Correct Extension

```python
# ✓ Lag module: PP carries markers, NF follows
class VEFWithLag(VEFStateEngine):
    def step(self, dt):
        # Evolve PP with lag
        self.pp_new = self._evolve_pp_with_lag(self.pp, dt)
        # NF follows PP
        self.nf_new = 1.0 - self.pp_new - self.void
        return self.state

# ✓ EOS module: Pressure from PP density
class VEFWithEOS(VEFStateEngine):
    def step(self, dt):
        # Evolve PP
        self.pp_new = self._evolve_pp(self.pp, dt)
        # Compute pressure from PP
        pressure = self._eos(self.pp_new)
        # NF follows PP
        self.nf_new = 1.0 - self.pp_new - self.void
        return self.state

# ✓ Shells module: PP curvature defines shell geometry
class VEFWithShells(VEFStateEngine):
    def step(self, dt):
        # Evolve PP
        self.pp_new = self._evolve_pp(self.pp, dt)
        # Compute shell geometry from PP curvature
        shell_geom = self._compute_shells_from_pp(self.pp_new)
        # NF follows PP
        self.nf_new = 1.0 - self.pp_new - self.void
        return self.state
```

---

## 🤝 Ways to Contribute

### 1. **Report Bugs**

Found an issue? Help us improve by reporting it:
- Check [existing issues](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues) first
- Create a [new issue](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues/new) with:
  - Clear title and description
  - Steps to reproduce
  - Expected vs. actual behavior
  - Your configuration (parameters, Python version, OS)
  - Example code if applicable

**Bug Report Template**:
```markdown
**Description**: Brief description of the bug

**Steps to Reproduce**:
1. ...
2. ...
3. ...

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Configuration**:
- Python version: 3.X
- OS: Windows/Mac/Linux
- VEF version: 1.0.0
- Key parameters: ...

**Code Example**:
```python
# Minimal reproducible example
```
```

### 2. **Suggest Features or Improvements**

Have an idea to make VEF better?
- [Open a Discussion](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions) to brainstorm
- Or [create a Feature Request Issue](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues/new?template=feature_request.md)
- Describe the use case and expected benefit
- **Explain how your feature respects PP–NF complementarity**
- Link to related research or physics concepts if relevant

**Ideas We're Interested In**:
- ✅ GPU acceleration (CUDA/OpenCL) — must preserve conservation
- ✅ Extended state variables (higher dimensions) — NF still derived from PP
- ✅ Alternative integration schemes (RK5, adaptive) — complementarity enforced at each step
- ✅ Interactive visualization tools (Plotly, Jupyter widgets)
- ✅ Performance optimizations — without breaking conservation
- ✅ Additional reference models
- ✅ Real-world application examples
- ✅ Educational materials and tutorials
- ✅ Physics modules (lag, EOS, radiation, shells) — **following Rule 5 above**

### 3. **Improve Documentation**

Clear docs benefit everyone:
- Fix typos or unclear explanations
- Add examples or use-case documentation
- Improve mathematical explanations
- Translate docs to other languages
- Create tutorials or notebooks
- **Clarify the PP–NF philosophy for new users**

### 4. **Submit Code Contributions**

Ready to code? We welcome pull requests for:
- Bug fixes
- New features (discuss first via issue/discussion)
- Performance improvements
- Test coverage expansion
- Code cleanup and refactoring

**All code must respect the Philosophy & Design Principles above.**

### 5. **Share Your Research**

Publishing work using VEF? Let us know!
- Add a link in [Research Applications](#-research-applications-using-vef)
- Share your findings and insights
- Cite the framework (see [Citation](#-citation))

### 6. **Provide Feedback**

- Star ⭐ the repo if you find it useful
- Share your experience in [Discussions](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions)
- Tell us what works well and what could improve
- Help answer questions from other users

---

## 🛠️ Development Setup

### Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/VEF-state-engine.git
cd VEF-state-engine
git remote add upstream https://github.com/markchrismanppnf-hash/VEF-state-engine.git
```

### Install in Development Mode

```bash
# Install with development dependencies
pip install -e ".[dev]"

# This installs:
# - vef-state-engine (editable)
# - numpy, matplotlib
# - pytest, pytest-cov (testing)
# - black (code formatting)
# - flake8 (linting)
# - mypy (type checking)
```

### Run Tests

```bash
# Run all validation tests
python vef_validation.py

# Run with pytest (if available)
pytest tests/ -v --cov=.

# Run full parameter sweep
python -c "from vef_validation import run_parameter_sweep; run_parameter_sweep()"
```

### Code Quality

```bash
# Format code with Black
black *.py

# Lint with flake8
flake8 *.py --max-line-length=100

# Type check with mypy
mypy vef_state_engine_improved.py --ignore-missing-imports
```

---

## 📋 Pull Request Process

### Before You Start

1. **Create an issue** for significant changes (discuss approach first)
2. **Review the Philosophy** above — does your change respect PP–NF complementarity?
3. **Check the roadmap** below for planned work
4. **Keep it focused** — one feature/fix per PR is best

### Making Your PR

1. **Create a feature branch**:
   ```bash
   git checkout -b fix/issue-description
   # or
   git checkout -b feature/new-capability
   ```

2. **Make your changes**:
   - Write clean, well-documented code
   - Add docstrings following NumPy style
   - Include type hints where applicable
   - Run tests to ensure nothing breaks
   - **Verify conservation: PP + NF + void = 1.0 everywhere**

3. **Commit with clear messages**:
   ```bash
   git commit -m "Fix: Brief description of what you fixed"
   git commit -m "Feature: Add new visualization type"
   git commit -m "Docs: Clarify parameter guidance"
   git commit -m "Physics: Add lag module (respects complementarity)"
   ```

4. **Push to your fork**:
   ```bash
   git push origin fix/issue-description
   ```

5. **Open a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to related issue (`Fixes #123`)
   - Summary of changes
   - **Statement of how changes respect complementarity** (if physics-related)
   - Any new dependencies or breaking changes
   - Test results showing validation passes

### PR Checklist

- [ ] Code follows Black formatting (`black *.py`)
- [ ] Passes flake8 linting (`flake8 *.py`)
- [ ] Type hints added (where applicable)
- [ ] Docstrings included (NumPy style)
- [ ] Tests pass (`python vef_validation.py`)
- [ ] No new warnings introduced
- [ ] Documentation updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] **Conservation verified: PP + NF + void = 1.0** (if code touches physics)
- [ ] **Complementarity maintained: NF always computed from PP** (if code touches physics)

### Review Process

- Maintainer will review your PR
- We may request changes or clarifications
- **For physics-related changes: verify philosophical alignment**
- Once approved, your PR will be merged
- You'll be credited in release notes!

---

## 📚 Code Style Guide

### Python Style

Follow **PEP 8** with Black formatting:

```python
# Good: Clear naming, type hints, docstrings
def compute_symmetry_index(pp: np.ndarray, nf: np.ndarray) -> np.ndarray:
    """Compute symmetry balance between modes.
    
    Args:
        pp: PP density values
        nf: NF density values
        
    Returns:
        Symmetry index array (0=perfect balance, 1=asymmetric)
    """
    epsilon = 1e-10
    return np.abs(pp - nf) / (pp + nf + epsilon)


# Avoid: Unclear names, no types, no docs
def symm(p, n):
    return abs(p - n) / (p + n + 0.0000000001)
```

### Docstring Style (NumPy Convention)

```python
def run_sequence(self, duration: float, dt: float = 0.01, 
                record_interval: int = 10) -> np.ndarray:
    """Execute simulation and record telemetry.
    
    Parameters
    ----------
    duration : float
        Total simulation time in seconds
    dt : float, optional
        Integration timestep (default: 0.01)
    record_interval : int, optional
        Record every N steps (default: 10)
        
    Returns
    -------
    np.ndarray
        Recorded data array of shape (n_records, 7)
        
    Raises
    ------
    ValueError
        If duration is negative
        
    Examples
    --------
    >>> recorder = VEFTelemetryRecorder(engine)
    >>> data = recorder.run_sequence(duration=100.0)
    >>> print(data.shape)
    (1001, 7)
    """
```

### Comments and Clarity

```python
# ✓ Good: Explains WHY, not WHAT
# Phase modulation: sin(φ) creates natural on-off switching
# This matches physical coupling behavior
coupling = alpha * np.sin(phase) * nf

# ✗ Avoid: Obvious comments
# Multiply alpha by sin(phase) and nf
coupling = alpha * np.sin(phase) * nf
```

---

## 🗺️ Roadmap & Known Opportunities

### Short-term (v1.1)
- [ ] Jupyter notebook tutorials with interactive examples
- [ ] Scipy integration for alternative ODE solvers
- [ ] Extended validation metrics (Lyapunov exponents, etc.)
- [ ] Batch simulation utilities for parameter sweeps
- [ ] Export to common data formats (CSV, HDF5)

### Medium-term (v1.2-1.5)
- [ ] GPU acceleration (CuPy/Numba) — preserving conservation
- [ ] Physics modules: **Lag** (PP carries markers, NF follows)
- [ ] Physics modules: **EOS** (pressure from PP density)
- [ ] Physics modules: **Radiation** (PP absorbs/emits, NF forms boundaries)
- [ ] Physics modules: **Shells** (PP curvature defines geometry, NF complements)
- [ ] Higher-dimensional state spaces (still maintaining complementarity)
- [ ] Real-time visualization (Plotly/Dash)
- [ ] Sensitivity analysis tools

### Longer-term (v2.0+)
- [ ] C/C++ backend for performance
- [ ] Multi-mode coupling (>2 modes, with consistent complementarity)
- [ ] Stochastic dynamics (optional, opt-in only)
- [ ] Integration with simulation ecosystems
- [ ] PyPI package distribution

**Interested in any of these?** [Let's discuss!](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions)

---

## 💬 Communication Channels

### Get Help or Discuss

1. **GitHub Issues** — Bug reports and feature requests
   - [View open issues](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues)
   - [Create a new issue](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues/new)

2. **GitHub Discussions** — Q&A, ideas, general chat
   - [View discussions](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions)
   - [Start a new discussion](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions/new)
   - Categories:
     - 💡 **Ideas**: Feature suggestions
     - ❓ **Q&A**: Usage questions
     - 💬 **General**: Off-topic chat
     - 📢 **Announcements**: Project updates

3. **Email** — For sensitive issues or private collaboration
   - Contact: markchrismanppnf@gmail.com
   - Subject: "VEF State Engine: [Your Topic]"

### Response Time

- **Issues**: 1-3 days (weekdays)
- **Discussions**: 2-5 days
- **PRs**: 3-7 days for review
- **Emails**: 1 week

---

## 🎓 Collaboration Ideas

### Active Areas Looking for Contributors

**Physics & Math**
- [ ] Develop lag module (PP carries Lagrangian markers)
- [ ] Develop EOS module (pressure from PP density)
- [ ] Develop radiation module (PP absorbs/emits)
- [ ] Develop shells module (PP curvature → shell geometry)
- [ ] Analyze bifurcations and attractors
- [ ] Verify against published coupled oscillator literature
- [ ] Develop new reference models
- [ ] Extend to stochastic regime (maintaining complementarity)

**Software Engineering**
- [ ] Performance profiling and optimization
- [ ] Continuous integration setup (GitHub Actions)
- [ ] Documentation automation
- [ ] Packaging and distribution

**Applications**
- [ ] Real-world data fitting examples
- [ ] Domain-specific modules (optics, quantum, mechanical systems)
- [ ] Educational materials for physics courses
- [ ] Interactive visualizations

**Community**
- [ ] Tutorials and blogs
- [ ] Video explanations
- [ ] User surveys and feedback
- [ ] Growing the user base

---

## 📜 Citation & Acknowledgment

If you use VEF State Engine in your research:

```bibtex
@software{vef_state_engine_2024,
  title={Volume-to-Force Differential State Engine},
  author={Chrisman, Mark},
  year={2024},
  version={1.0.0},
  url={https://github.com/markchrismanppnf-hash/VEF-state-engine},
  note={Physics simulation framework for coupled oscillatory systems with PP-NF complementarity}
}
```

**Contributors** will be acknowledged in:
- Release notes for your PR
- [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- This README under "Special Thanks"

---

## 🙏 Special Thanks

VEF State Engine is better because of contributions from:

*Contributors will be listed here as they join the project!*

---

## 📝 Additional Resources

- **Main README**: [README.md](README.md)
- **Technical Docs**: [VEF_DOCUMENTATION.md](VEF_DOCUMENTATION.md)
- **GitHub Issues**: [markchrismanppnf-hash/VEF-state-engine/issues](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues)
- **GitHub Discussions**: [markchrismanppnf-hash/VEF-state-engine/discussions](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions)
- **GitHub Repository**: [github.com/markchrismanppnf-hash/VEF-state-engine](https://github.com/markchrismanppnf-hash/VEF-state-engine)

---

## 📄 License

By contributing to VEF State Engine, you agree that your contributions will be licensed under its MIT License.

---

## ✨ Thank You!

Whether you report bugs, suggest features, improve docs, or submit code — **every contribution matters**. Thank you for helping make VEF State Engine better! 🚀

---

**Questions?** [Start a discussion](https://github.com/markchrismanppnf-hash/VEF-state-engine/discussions) or [open an issue](https://github.com/markchrismanppnf-hash/VEF-state-engine/issues) — we're here to help!
