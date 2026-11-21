# What a water calculation must conserve

A parcel can spin faster when drawn toward a vortex axis. It need not become much denser. The question is whether the surrounding water can stretch a rotating column fast enough to overcome viscous spreading, how long the column stays coherent, and where the energy comes from.

Use single-phase, Newtonian, heat-conducting ordinary water in local thermodynamic equilibrium. For the reference geometry neglect gravity, free surfaces and dissolved gas dynamics. Use SI and **absolute** thermodynamic pressure. The physical model has no body-force or volume-heat-source terms. In a fixed control volume with outward unit normal **n**, the differential conservation laws are

```text
∂t ρ      + div(ρu)                         = 0
∂t (ρu)   + div(ρu⊗u + pI − τ)              = 0
∂t (ρE)   + div[(ρE+p)u − τ·u + q]          = 0
E = e + |u|²/2                  q = −k grad T
D = (grad u + grad uᵀ)/2        θ = div u
τ = 2μ(D − θI/3) + ζθI
```

Here μ and ζ are shear and bulk viscosity (Pa s), k is thermal conductivity (W/(m K)), and e is specific internal energy (J/kg). Viscous dissipation Φ = 2μ|D − θI/3|² + ζθ² converts mechanical to internal energy. The local internal-energy balance is ρ De/Dt = −pθ + Φ − div q. Rigid rotation can have high vorticity and zero viscous heating. Use measured shear viscosity. A baseline ζ = 0 is an explicit Stokes hypothesis for the slow swirl comparison. Acoustic **attenuation** or significant dilatation requires a justified bulk-viscosity model and sensitivity check.

**Thermodynamic closure.** Use a vetted library for the IAPWS-95 Helmholtz free energy f(ρ,T). Then p = ρ²(∂f/∂ρ)ₜ and e = f − T(∂f/∂T) at fixed ρ. Invert e(ρ,T) on the liquid branch after removing kinetic energy from E. This gives mutually consistent pressure, temperature, heat capacities, expansion and isentropic sound speed c² = (∂p/∂ρ)ₛ. CoolProp's Water backend is one independent implementation. Check round trips (p,T) → (ρ,e) → (p,T), derivatives, phase and transport near the actual run states. A pressure-only Tait fit cannot recover heating. The 0.1 MPa correlations are convenient reference values, while a transient compressible run needs the pressure dependence too. [IAPWS-95](https://iapws.org/technical-guidance/release/IAPWS-95) · [CoolProp Water](https://coolprop.org/fluid_properties/fluids/Water.html)

**Working values.** At 293.15 K and about 101325 Pa use rounded ρ = 998 kg/m³, ν = 10⁻⁶ m²/s, μ = ρν ≈ 0.998 mPa s, c = 1480 m/s, cₚ ≈ 4180 J/(kg K), k ≈ 0.60 W/(m K) and saturation pressure ≈ 2340 Pa. The analytic benchmark holds coefficients fixed. Record the library values in a physical run and compare at its actual ν. [IAPWS liquid properties near 0.1 MPa](https://iapws.org/technical-guidance/release/LiquidWater) · [IAPWS saturation properties](https://iapws.org/technical-guidance/release/Supp-sat)

**Budgets for each stored interval.** Integrate mass, vector momentum, angular momentum about the vortex axis, kinetic energy and internal energy. Reconcile storage with the signed time-integrated face fluxes above. Include moment of traction and advected angular momentum. For a face moving at w replace the advecting normal speed by (u−w)·n in the mass, momentum and ρE terms. Keep pressure and viscous work at the fluid velocity. An impermeable no-slip wall supplies power ∫u_wall·(−pI+τ)n dA. In an adiabatic closed stationary vessel total energy is constant while kinetic energy can become heat. For ports include enthalpy, kinetic, traction and heat fluxes and measure flow and pump power. Normal reactions can exchange momentum even when a wall does zero work.

**When to stop interpreting single-phase results.**

| Observation | Interpretation |
|---|---|
| Local minimum of p_abs − p_sat(T) approaches its pressure uncertainty or crosses zero | Flag location and duration and stop the liquid-only extrapolation. Nuclei, gas content and pressure history govern inception. An observed vapor volume or gas entrainment invalidates the homogeneous-liquid description. A single-phase solver cannot report bubble growth. |
| Coherent propagating p′ and dilatation, correlated ρ′ and travel time L/c | Separate acoustic motion from a slowly balanced radial pressure gradient. Examine pressure spectra and reflection times under time-step refinement. Thermal expansion can also cause density change. |
| Resolved T rise, Φ, pressure work or wall heat flux | Compare local μ(T), ν and p_sat(T) with their starting values. Close the heat budget before attributing a change in spreading to temperature. |
| Gradients localize toward the molecular correlation length or transients toward molecular relaxation times | Seek independent material length/time data and a molecular or non-equilibrium description. Millimetre core radii alone give no continuum cutoff. |

For actual vertical measurements restore hydrostatics at the probe elevation (ρg × 1 cm ≈ 98 Pa, larger than the example swirl signal). A measured phase boundary, instability or loss of resolution answers a different question in each case. [Brennen, *Cavitation and Bubble Dynamics*](https://media.library.caltech.edu/CaltechBOOK:1995.001/chap1.htm)
