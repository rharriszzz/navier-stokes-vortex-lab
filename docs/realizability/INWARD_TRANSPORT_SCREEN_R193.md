# Inward transport and tangential response — R193

R195 update: [verification source and fixture algebra](NONLINEAR_VERIFICATION_R195.md)
are complete; FEM remains untested. Earlier next-step recommendations below are
historical. Follow the single [current task](../../SESSION_HANDOFF.md#next-task)
for the small cube adapter/review, stopping before FEM imports or execution.

2026-09-22; PC/WSL `daisy`. **Inward transport can defeat quiescent diffusion
attenuation in a comparison equation, but the available information cannot
bound either actuator's actual gain. Neither route is admitted.** The missing
quantities are wall-to-stream entrainment, connected meridional paths, swirl
phase dispersion, coupled velocity/pressure response and complete-face transfer.
A fast bore velocity or a large Péclet number does not supply those quantities.

This completes the bounded analytical screen requested by R192. It is a
source/algebra/design result, with no tank solve or physical run. R191's
[phase-test contract](ESSENTIAL_SIMILARITY_CONTRACT_R191.md) and R192's
[operating point](FIXED_CORE_OPERATING_POINT_R192.md) remain conditional.
All comparison formulas, numbers and proposed error tests below are our
calculations; none is a calibrated response. The single
[next task](../../SESSION_HANDOFF.md#next-task) now concerns the base-flow problem.

## Geometry and information actually available

Use R192's vessel radius 100 mm, half-height 100 mm, diagnostic R=H=25 mm,
water nu=1e-6 m²/s, two bands at |z|=45–75 mm, f=0.1 Hz and m=4. The nearest
band point to the diagnostic surface is at its rim, not at its midplane:

| Distance or time scale | Value | Interpretation |
|---|---:|---|
| Radial gap only | 75 mm | Omits the axial offset. |
| Nearest band edge to diagnostic rim | 77.621 mm | sqrt(75²+20²); lower geometric distance, not a streamline. |
| Band centre to diagnostic rim | 82.765 mm | sqrt(75²+35²); actual ports can be staggered within the band. |
| Nearest band edge to equatorial swirl peak | 99.543 mm | Uses r_c=11.209 mm; distinct from delivering to the budget surface. |
| Nearest-distance diffusion scale L²/nu | 6025 s | Not settling time or actuator bandwidth. |
| Vessel volume / loop flow, wall / ports | 188.496 / 94.248 s | Inventory turnover only; may include short circuits. |

The conditional interior U_r=-0.02r, U_z=0.04z and Gaussian swirl are known
only as a target description. Neither pump total nor central throughput
specifies the surrounding velocity. Both band rings may feed cap returns
without feeding the diagnostic cylinder. Paths can bend, stagnate, recirculate
or traverse the central caps; their lengths, dwell times and weights are unknown.

An instructive **invalid extrapolation**, evaluated only to expose its failure:
extending that linear strain from r=100 to 25 mm gives a nominal radial travel
time log(4)/0.02=69.315 s. But its invariant is z*r²=constant. Starting at
z=60 mm reaches z=100 mm after 12.771 s at r=77.460 mm, before reaching the
central radius; z would become 960 mm at r=25 mm. Even this extrapolation
misses the central cylinder. No such field is imposed on the tank here.
The Burgers model's imposed background strain is explicitly part of its
infinite-domain setting, as reviewed by
[Gallay–Maekawa, Section 1](https://arxiv.org/html/1002.2489#S1).

## Governing coupling before any scalar reduction

Assume provisionally a steady axisymmetric incompressible base
U=(U_r,U_theta,U_z), maintained by the physical boundary conditions with no
azimuthal body force. This assumption must itself be checked: the discrete
ports create nonaxisymmetric base structure. Let v,p' be small perturbations,
Omega=U_theta/r, L_b=r*U_theta, ell=r*v_theta, and
D_b=partial_t+U_r*partial_r+U_z*partial_z+Omega*partial_theta.
Linearizing the cylindrical azimuthal momentum equation gives, for e^(im theta),

```text
D_b ell + v_r*partial_r L_b + v_z*partial_z L_b
 = -i*m*p'/rho
   + nu*(partial_rr ell - (1/r)*partial_r ell + partial_zz ell
         - (m²/r²)*ell + (2*i*m/r)*v_r).
```

This is our transformation of the cylindrical Navier–Stokes equation in
[Sonin's MIT notes, Appendix A](https://web.mit.edu/2.25/www/pdf/viscous_flow_eqn.pdf).
Pressure has no *integrated* axial torque on the central cylindrical surface;
it still redistributes nonaxisymmetric angular momentum locally. Thus the
pressure term above cannot be discarded using the integral torque argument.
The radial/axial momentum equations and incompressibility close this system.
For a nonaxisymmetric or time-dependent base, Fourier modes or frequencies
couple; a single diagonal m=4 transfer function is then insufficient.

Dropping p', v_r, v_z coupling is generally unjustified for this test: normal
forcing is intentional, and nonzero m=4 tangential velocity alone is not
divergence-free. In the special inviscid, uncoupled angular-momentum transport
limit ell is carried along paths, so v_theta can grow as 1/r. A scalar ell gain
is not a velocity gain; the geometric conversion from wall to R would be 4
for an ideal connected path. This factor does not establish a bound in the
coupled problem. R192's 2 mm/s target is four times the conditional radial mean
at R, so small amplitude relative to swirl does not establish linearity.

## Exactly soluble transport comparison

To isolate advection versus diffusion, define an artificial constant-coefficient
scalar q on a straight semi-infinite path s>=0. It has no curvature, pressure,
velocity coupling, shear amplification or return boundary:

```text
partial_t q + V*partial_s q + Omega_* * partial_theta q
 = nu*partial_ss q - nu*k_perp²*q,       V >= 0.
q(0,theta,t) = Re[q0*exp(i*m*theta-i*sigma*t)],  sigma = +omega or -omega.
Delta = m*Omega_* - sigma;   omega = 2*pi*f.
q/q0 = exp(i*m*theta-i*sigma*t-kappa*s),
kappa = (sqrt(V²+4*nu*(nu*k_perp²+i*Delta))-V)/(2*nu).
```

Choose the square root with nonnegative real part and the bounded downstream
solution (constant if Delta=k_perp=0). The retained checker uses the equivalent
rationalized root. The amplitude ratio is exp(-Re(kappa)*L), and the spatial
phase shift is -Im(kappa)*L. This is exact for this scalar equation only.
With V=Omega_*=k_perp=0, it recovers the Stokes penetration length 1.784 mm
and gain 1.27e-19 at L=77.621 mm. R192's 5.54e-19 used the shorter 75 mm gap.

For sufficiently strong transport, |nu*k_perp²+i*Delta|*nu/V² << 1,

```text
kappa approximately (nu*k_perp²+i*Delta)/V
                   - nu*(nu*k_perp²+i*Delta)²/V³.
Re(kappa) approximately nu*k_perp²/V + nu*Delta²/V³
```

The second line additionally neglects the smaller transverse-diffusion square.
Advection moves temporal phase gradients to wavelength about 2*pi*V/|Delta|;
diffusion still damps those gradients. Pe=V*L/nu alone cannot quantify that loss.
Useful additional parameters are |Delta|*L/V, nu*|Delta|/V²,
nu*k_perp²*L/V, curvature L/r and the variation of the base over an attenuation
or phase length. Here L/r is not small along the complete wall/core gap.

The following is a **sensitivity table**, not a fitted transport tube. Column 1
uses Omega_*=0 and k_perp=0. Columns 2–3 freeze the *local central-side target*
Omega_R=1.251159 rad/s and k_perp=m/R=160 m^-1 over the entire artificial path.
That deliberate comparison does not assert those coefficients in the exterior.

| V (mm/s) | Pe | L/V (s) | No swirl scalar gain | Frozen side, sigma=+omega | Frozen side, sigma=-omega |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | — | 1.27e-19 | 9.73e-51 | 1.98e-57 |
| 0.5 | 38.8 | 155.24 | 3.72e-12 | 1.14e-42 | 2.57e-49 |
| 2 | 155.2 | 38.81 | 0.03218 | 5.06e-23 | 5.96e-29 |
| 5 | 388.1 | 15.52 | 0.7832 | 2.10e-5 | 7.21e-8 |
| 10 | 776.2 | 7.76 | 0.9698 | 0.1884 | 0.07281 |
| 20 | 1552.4 | 3.88 | 0.9962 | 0.7520 | 0.6658 |

Gain 0.1 occurs at respectively 2.3204, 8.8916 and 10.4740 mm/s in these three
comparison equations. These are neither necessary nor sufficient tank-speed
requirements, and cannot be substituted for R192's boundary-to-core gains.
They do demonstrate why the no-advection wall estimate cannot exclude the
circulating-wall route and why merely adding nominal inflow cannot admit it.

## Standing modes, shear, path spread and wall entrainment

R192's standing input cos(m theta)*cos(omega t) equals one half the sum of
cos(m theta-omega t) and cos(m theta+omega t). Retain both traveling components.
In the local conditional core, the two Doppler detunings are:

| Position | Omega (rad/s) | m*Omega-omega (rad/s) | m*Omega+omega (rad/s) | r²/(nu*m²) (s) |
|---|---:|---:|---:|---:|
| Diagnostic side R=25 mm | 1.251159 | 4.376318 | 5.632955 | 39.0625 |
| Swirl peak r_c=11.209 mm | 4.460676 | 17.214384 | 18.471021 | 7.8527 |

The last column is a local azimuthal diffusion time, not a transit or response
time. Even in an axisymmetric base, the two traveling responses differ, so the
interior need not retain a separable cos(m theta+phi)*cos(omega t+delta) shape.
A radius at which one component nearly corotates does not rescue the other or
eliminate axial/radial diffusion. No critical-layer calculation is claimed.

In an advection-dominated path approximation, phase accumulates as
integral(m*Omega-sigma) dt. Angular shear, travel-time spread and uncertain
paths change this integral and create transverse gradients that diffuse.
A schematic sum of connected paths has factors
w_j*E_j*exp(-integral nu*k² dt)*exp(-i*integral Delta dt), where E_j includes
entrainment and the angular-momentum/velocity conversion. This is explanatory,
not a closure model: its weights and operators are unknown. Two equal paths
with phase difference pi cancel even with negligible molecular attenuation.
Consequently a short mean transit time gives no positive lower gain bound.
Pressure/shear coupling also prevents a passive-scalar upper bound for velocity.

A deterministic delay can be compensated after calibration; uncertain delay
cannot. R192's five-degree drive-timing allocation is 139 ms at 0.1 Hz. In the
frozen-side path comparison, five degrees of accumulated material-phase error
corresponds to only 19.94 or 15.49 ms of path-time error, or to
|m*integral delta(Omega)dt|<=0.0873 if swirl error alone is allocated. These are
sensitivity illustrations, not added universal timing gates. A long stable delay
need not erase coherence; path variability and settling must be measured.

**Moving belt:** no penetration holds on each solid moving patch, so V is zero
at its surface in the normal direction. A uniform inward V cannot start at
that belt. Viscous traction must first transfer modulation to adjacent fluid,
which nearby normal jets may entrain. The extraction-layer thickness, tangential
residence time, separation, gaps and wall-to-stream phase/gain are unknown.
Subsequent rapid transport cannot restore a signal already lost at this stage.
One cannot combine the wall's Dirichlet speed with through-wall inlet advection
on the same solid patch. A porous moving-wall comparison would be a different
hardware design.

**Ports:** the trial 2 L/min per 32 bores gives 82.893 mm/s bore speed; an angled
bore has 58.613 mm/s inward radial component. Dividing the nearest distance by
these speeds gives 0.9364 and 1.3243 s. These are distance/speed ratios only,
not first arrivals, bounds or settling times. Jet entrainment, spreading,
rotation and the required axial turn invalidate constant-speed delivery. Both
proposed inlet directions initially have zero axial component and retain their
band height without turning; straight radial or angled paths miss the central
cylinder. Balanced returns can short-circuit them. Ports nevertheless inject
tangential momentum with incoming fluid and avoid the solid-belt extraction
step, supporting R192's port-first study priority without selecting hardware.

## What would turn the screen into a defensible bound

At minimum, obtain the realized base and uncertainty across the bands, gap,
central side/caps and return paths: all three velocity components, gradients,
unsteadiness/nonaxisymmetric content, viscosity, per-port profiles and boundary
traction. Establish connected transport and its residence/phase distribution;
quantify the wall entrainment operator for a wall claim. Resolve both m=4
traveling components, actual finite footprints, and leakage to other modes.
Record base pressure or consistent traction and the base momentum residual.

A reduced prediction needs a quantified discrepancy, not only a PDE residual.
For a genuinely passive stable scalar with homogeneous error boundary/initial
data, a bounded forcing residual R gives the maximum-principle error estimate
||e(T)||_infinity <= integral_0^T ||R(t)||_infinity dt. Include nonzero boundary
and initial errors if present. This does **not** apply to ell's neglected
pressure/velocity terms as if they were known: their magnitudes are unmeasured.
For the full coupled linearized flow, with an admitted evolution bound
||S(t,s)||<=M*exp(gamma*(t-s)), one would instead propagate initial, boundary,
base and residual errors through that bound and the actual observation operator.
M, gamma and the surface-gradient observation errors are currently unknown.
Nonlinear remainder must also be bounded or checked with amplitude scaling.

Map the resulting complex response intervals to the *complete surface* stress
contrast, including both caps and cross-components. A simple side-mode
normalization needs |G_rn| about 0.10 and tangential gain about 0.10 (wall) or
0.1414 (angled tangential component), but shape, phase and cap cancellation
can defeat those individual thresholds. Scalar attenuation cannot determine
R192's eta or the sign of the net transfer.

To retain R192's fixed error allocations, the conservative resolved contrast
must reach |D|=39.270 micro-N m s over 100 s. Its full residual and independent
external-confound uncertainties must each meet the one-third criterion; the
nominal external mean-torque allowance is 0.130900 micro-N m. The covariance
contrast allocation remains 1.528e-7 m²/s². Model/base uncertainty must fit
within the combined budget, not be added outside it. If the actual contrast is
smaller, tighten allocations to its magnitude and report the reduced target.
No torque, optical or cap gate is satisfied by a large transport gain alone.

## Decision and minimal next calculation

R194 completed the [base-flow boundary and verification contract](PORT_BASE_FLOW_CONTRACT_R194.md).
Only a separate verification prototype is admitted next; no tank implementation,
CFD execution or hardware route is admitted. Follow the single
[current task](../../SESSION_HANDOFF.md#next-task). The original decision below
is preserved as historical context.


**This screen establishes mechanism sensitivity, not feasibility or exclusion.**
The quiescent wall result is not a finite-tank gain bound. Advection could help,
but the geometry, solid-wall injection condition, two traveling modes and
unbounded coupling prevent a justified gain interval. Neither route is admitted;
no achievable radius contraction or similarity-time range follows. B2 accuracy
remains failed, q64/q96 unused and R021 integration deferred.

The minimum discriminating calculation is a coupled normal/tangential response
at 0.1 Hz about an independently validated, boundary-driven base at this operating
point. Since that base does not exist in the present evidence, its construction
is the first prerequisite. Ports remain first for study; a wall claim later
requires its own base, entrainment and torque assessment.

**Next bounded task: specify and review the smallest credible port-driven
base-flow calculation.** Define flux-compatible finite port/return geometry,
normal and angled inlet profiles, return closure, fixed-wall conditions,
pressure gauge and preparation protocol, without prescribing the desired
Gaussian in the volume. Decide explicitly whether an axisymmetric averaged
boundary can be only a screening stage or has a quantified relation to the
sixteen-sector geometry. Identify a numerical-method/verification path for the
steady or statistically settled base, including mass, angular-momentum and
energy closure, central strain/swirl and exterior transport, and convergence
requirements for a later m=4 response. Audit existing solver capabilities and
failed B2 evidence before proposing reuse; a quiescent Stokes solve cannot
supply this advective base. Deliver a reviewable boundary/verification contract
with missing inputs and an implementation-admission decision. Stop before solver
implementation, dependency changes, CFD/FEM, procurement or physical execution.
Do not launch R192's full phase test automatically.

Later, only after that base is admitted, compare off and individual normal/
tangential drives at 0.01 and 0.02 m/s, retaining full complex velocities on all
central faces, endpoint inventories, surrounding transport and all external
angular input. Use both spatial quadratures where rotational symmetry is not
established. Check transient decay, amplitude scaling, harmonics and numerical
or measurement error before the paired phase test. This specifies the needed
response evidence without authorizing its execution.

Retain GPT-6 Astra/high on PC/WSL `daisy` for the unresolved model/method choices.
[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was rechecked through OpenAI Docs for high support. This is a task-fit judgment,
not verification of account access or quota. Recommend a cheaper model only
when implementation is mechanical, after rechecking availability; no switch.

[Retained arithmetic and identity checks](evidence/r193/README.md) passed fifteen
groups. Production code, pins, benchmark science, attempt budgets and saved
trajectories are unchanged; no task workload child was launched.
