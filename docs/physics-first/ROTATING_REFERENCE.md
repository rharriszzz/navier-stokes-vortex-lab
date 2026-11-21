# Viscous spreading against a rigid circular wall

A stationary no-slip cylinder requires zero azimuthal **velocity** at the wall. For regular swirl the diffusion equation is ∂ₜu = ν(u″ + u′/r − u/r²). Its modes are J₁(kᵢr), where kᵢR is a positive zero of J₁. There is no rigid-rotation mode. For R = 0.1 m we project the tapered initial profile with weight r dr, divide by R²J₀(kᵢR)²/2, and multiply each coefficient by exp(−νkᵢ²t). Vorticity uses kᵢJ₀ and wall shear uses −kᵢJ₂. Density and transport are the wall-state CoolProp constants, ν = 1.0033951 × 10⁻⁶ m²/s. Centrifugal pressure follows from integrating ρu²/r. This is the incompressible mechanical comparator for the compressible disk. [Calculation](../../physics_first/no_slip_disk.py) · [Mode and quadrature comparisons](rotating-disk/reference.json)

| Time | Peak radius (mm) | Peak speed (m/s) | Axis vorticity (s⁻¹) | Inner 30 mm pressure rise (Pa) |
|---:|---:|---:|---:|---:|
| Release | 10.00000 | 0.1000000 | 35.1288 | 15.90532 |
| 1 ms | 10.00025 | 0.0999975 | 35.1270 | 15.90446 |
| 20 ms | 10.00504 | 0.0999496 | 35.0933 | 15.88820 |

The 1 ms peak migration is about **0.25 µm**, and the kinetic loss is 0.1671 µJ per metre of cylinder. The wall does no mechanical work. The predicted energy loss is the integral of 2πμr(u′−u/r)² over radius and time. Angular momentum changes at the rate 2πμR²(u′−u/R) at the wall. Directly differentiating the projected angular momentum reproduces this wall torque. Its tiny nonzero release value in the truncated series measures reconstruction error since the actual profile vanishes outside 80 mm.

The unbounded Lamb–Oseen solution with width squared a²+4νt supplies a second, inner comparison. Its untapered tail differs outside 60 mm. The diffusion length in 1 ms is 0.063 mm. The 256-mode, 4096-point maximum inner discrepancies at 1 ms are 1.1 × 10⁻⁸ m/s in velocity and 1.6 × 10⁻⁴ s⁻¹ in vorticity. Use changes evaluated with the same truncation and inspect the 128/256-mode sensitivity. R277 used positive zeros of J₂ and a rigid-rotation mode to enforce zero wall shear. Its torque-free angular-momentum budget belongs to that boundary alone. [Original R277 result](SPREADING_RESULT.md)

Reproduce with the water Python and SciPy environment documented for R283. Run `python -m physics_first.no_slip_disk` and `python -m unittest tests.test_rotating_disk` from the repository root.
