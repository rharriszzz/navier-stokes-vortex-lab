# Cost versus captured dynamics in water — R202/R203

[The consolidated essay](WATER_EXPERIMENT_FEASIBILITY_AND_COST.md) covers the
physical outlook, ideal-instrument limits and both cost routes in one narrative.
This file retains the more detailed supporting analysis.

Planning estimates dated 2026-09-22; clarity review R204. Companion to the
[water outlook](WATER_EXPERIMENT_OUTLOOK_R200.md). All costs are **US dollars**.
Published component prices support the estimates, but complete apparatus and
pressure-vessel costs remain unquoted. No experimental range has been demonstrated.

**Start at atmospheric pressure and pay first for useful measurements.** I
would begin with a **$3,000–8,000 feasibility bench**, or **$1,000–4,000 of
additional equipment in a suitably equipped lab**. If it establishes useful
boundary control and sensing, the next ambition is a measured contraction from
roughly 10 mm to 3 mm. Budget approximately **$12,000–35,000 from scratch** or
**$5,000–18,000 with suitable lab equipment already available** for that apparatus.
These amounts exclude research labor and facility fees.

Reaching 1 mm with convincing measurements is a substantially more expensive,
uncertain research goal. Proving that the imposed perturbations cause a net
momentum transfer is also a separate expense: a visible contracting vortex does
not establish that mechanism. Extra pressure helps only when low absolute
pressure limits a flow that the actuators can already create and sensors can
already measure.

## What counts as a captured result

The goal is a finite analogue with measured contraction, spin-up, coupled
radial/axial motion and competition with viscosity. The stronger mechanism claim
requires showing how the perturbations change the momentum balance. Cost cannot
be translated into a percentage of the original mathematical solution.

Here, **core radius** means the radius of the measured swirl-speed peak.
If radius follows the illustrative square-root relation to remaining similarity
time, 10→3 mm is about **one decade in similarity time**, 10→1 mm is **two**,
and 10→0.1 mm is **four**. A decade means a factor of ten in that time variable,
not in radius. This conversion is conditional: report measured radii and elapsed
seconds unless the scaling is established. The
[experimental criteria](ESSENTIAL_SIMILARITY_CONTRACT_R191.md) define the evidence
needed for each claim.

## Atmospheric-pressure options with real instruments

Each row is an **alternative total equipment budget for that capability**.
Do not add the rows together. The lab column is the additional cash outlay when
suitable instruments are already available; it does not include their existing
value. Both columns exclude research labor and facility fees.

| Intended capability | Buy from scratch | Add to a suitably equipped lab | Scientific target and confidence |
|---|---:|---:|---|
| Small feasibility bench | $3k–8k | $1k–4k | Test a few boundary inputs and basic pressure/velocity measurements. No contraction range promised. |
| Modest contraction apparatus | $12k–35k | $5k–18k | Pursue 10→3 mm contraction and spin-up. Cautious optimism; full mechanism attribution requires more evidence. |
| Quantitative 3D mechanism study | $40k–120k | $20k–65k | First measure phase-dependent momentum transfer at a fixed core size. Success adds evidence about the mechanism, not necessarily more contraction. |
| Quantitative contraction toward 1 mm | $80k–250k | $40k–150k | Pursue 10→1 mm with resolved central and surrounding flow. An uncertain research target, even at this budget. |
| Submillimetre research program | $250k–750k+ | $150k–500k+ | Explore below 1 mm, perhaps toward 0.1 mm, with substantial redesign. A program allowance, not a prediction of attained range. |

The mechanism study and the 1 mm extension are **different research directions**,
not mandatory consecutive purchases. The first asks whether changing the relative
phase of boundary inputs produces a measurable net momentum transfer; the second
asks how far a coherent vortex can contract while remaining measurable. Combining
both goals requires evaluating their joint equipment and error requirements.

The modest apparatus assumes a few independently controlled mean-flow groups
feeding many ports. The mechanism study instead needs multiple independently
phased inputs, three-dimensional velocity measurements and momentum accounting
through the top, bottom and sides of the observed region, plus the surrounding
fluid and external inputs. Limited camera views can support preliminary
contraction measurements but cannot establish that complete balance.

Atmospheric pressure means near-atmospheric **background pressure in the test
region**. Pumps still need differential pressure to overcome plumbing losses.
A vented reservoir can set the background while the viewed tank is filled;
a free surface in the core region is not required. Removing bubbles and
controlling temperature remain real tasks at every budget level.

## What the equipment budgets include

**From scratch:** project equipment, a modest computer, purchased fabrication,
assembly materials, calibration fixtures, an optical enclosure where needed,
and roughly 25% equipment contingency. A suitable room, utilities and owner or
researcher integration effort are assumed. This is not a turnkey research contract.

**Equipped lab:** the imaging system, illumination, synchronization, software,
computer, data-acquisition equipment (DAQ), temperature equipment and workshop
resources needed for that particular row are already available. A lab with one
ordinary camera does not qualify for the volumetric-imaging discount. Existing
instruments and salaried staff still have an economic cost, even when they do
not require new cash spending.

Neither column includes taxes, shipping, institutional overhead, room renovation,
research labor or facility-use charges. Those costs must be added where applicable.
The ranges describe alternative configurations and uncertain estimates; they are
not guaranteed ceilings. The included 25% contingency covers some equipment
changes. Larger scope or custom-design surprises could still change the estimate
by roughly a factor of two, especially for the submillimetre and pressure options.

## Where a modest apparatus budget goes

Illustrative allocation for the $12k–35k from-scratch row. These are planning
allowances, not six vendor quotes:

| Item | Equipment/fabrication allowance | What it buys and what remains unproven |
|---|---:|---|
| Atmospheric vessel, optical access, supports and port fabrication | $1k–3k | A modest transparent test section; no pressure-vessel rating implied. |
| Recirculation, returns, plumbing, flow readbacks and swirl supply | $2k–5k | A small number of mean-flow circuits; actual required flow and loss remain unknown. |
| Approximately 4–8 controlled flow channels, drivers and manifolds | $2k–6k | Adjustable mean driving and limited response tests; not 64 independent port commands. |
| Approximately 2–4 pressure channels, conditioning and calibration provisions | $1k–4k | Hydraulic diagnostics and core-state cross-checks; sub-pascal inference is not assured. |
| One/two cameras, lenses, illumination, mounts, tracer and calibration supplies | $3k–7k | A custom slow-flow optical system; not a turnkey high-speed volumetric PIV package. |
| Computer, DAQ/timing and basic temperature monitoring/control | $1k–3k | Limited channel count and modest processing; revisit if actual acquisition/thermal load exceeds it. |
| Subtotal | $10k–28k | Before contingency. |
| Approximately 25% equipment contingency | $2.5k–7k | Calculated total $12.5k–35k; abbreviated as roughly $12k–35k elsewhere. |

Lower endpoints assume economical choices and substantial owner integration.
The equipped-lab version reuses its cameras, optics, computer, DAQ and
temperature equipment, but still needs the flow apparatus and calibrated controls. A high-end turnkey laser/PIV purchase would put this row outside its
stated budget. LED illumination and offline processing are candidates for the
slow initial tests; their photon budget and measurement bias must be checked.

Public component-price references checked for R202 on 2026-09-22:

| Actual published price or observation | How it informs the estimate |
|---|---|
| Selected Bürkert Type 2875 variants list **$435 brass / $524 stainless** on the US manufacturer page. [Product/pricing](https://www.burkert-usa.com/en/type/2875). | One valve is only part of a controlled channel. Eight valves alone are $3,480–4,192; 32 are $13,920–16,768; 64 are $27,840–33,536. Drivers, manifolds, flow calibration and compatible pressure/orifice choices are additional. |
| LabJack lists **T7 $570, T7-Pro $850, T8 $1,400**. [Current device listings](https://labjack.com/collections/t-series-devices). | DAQ need not dominate a small bench. Additional output channels, conditioning and synchronized acquisition still cost money; headline ADC resolution is not sensor accuracy. |
| A US distributor lists the Dwyer 629C wet/wet transmitter **from $550.90**. [Seller listing](https://usa.alphacontrols.com/products/629c-wet-wet-differential-pressure-transmitter). | A plumbing-sensor price anchor only. Its advertised 0.5% accuracy does not establish suitability for a roughly 1 Pa signal or R192's differential error budget. |
| Kron's comparison page lists Chronos **1.4 from $4,500; 2.1-HD from $6,800**. [Manufacturer comparison](https://www.krontech.ca/product-comparison/). Prices are USD on the [camera catalog](https://www.krontech.ca/product-category/cameras/). | Four 2.1-HD bodies already start at $27,200 before lenses, illumination and synchronization. Configuration can cost more. The listed finite recording times are not 100 s continuous acquisition. |
| A 2024 research build reports a **$520.50** hardware BOM for a low-cost planar PIV system. [Authors' paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11362640/). | Historical proof that exploratory imaging can be inexpensive, not a current quote or validation of our 3D stress measurement. Its restricted planar demonstration is materially less demanding. |

The [manufacturer's 1920×1200, 163 fps global-shutter camera specification](https://www.teledynevisionsolutions.com/products/blackfly-s-usb3/?model=BFS-U3-23S3M-C&segment=iis&vertical=machine+vision)
illustrates another camera class for slow experiments; no verified price is
assigned here. Particle image velocimetry (PIV) and particle tracking velocimetry
(PTV) use images of tracers to estimate velocity. Complete three-dimensional
systems also need suitable illumination, synchronization, calibration and
processing. Those system quotes are still missing. Camera price or pixel count
alone does not establish the accuracy of measured velocity correlations.

## What additional pressure actually buys

**Pressure postpones cavitation; it does not improve every experimental limit.**
In the earlier Gaussian-vortex illustration, the swirl-induced pressure drop
is only about 47 Pa at a 3 mm width and 425 Pa at a 1 mm width. Those widths
correspond to measured peak radii of about 3.36 mm and 1.12 mm. Atmospheric
pressure therefore leaves substantial margin in this particular calculation.
Actual nozzle, return and transient suction still need measurement.

At fixed circulation and profile, the cavitation cutoff radius decreases as
the inverse square root of the available pressure margin. Roughly doubling that
margin permits a radius about 1.4 times smaller. This is a benefit **only if
cavitation is the first limit reached**. If delivery stops at 1 mm, moving a
hypothetical cavitation cutoff from about 73 to 33 micrometres adds **zero
captured range**.

The following table applies the
[R201 Gaussian calculation](WATER_EXPERIMENT_OUTLOOK_R200.md#near-atmospheric-pressure-i-would-watch-for-cavitation-first).
Its core-radius column uses the same swirl-peak definition as the budget table.
These are theoretical cavitation thresholds, not achieved or promised radii.
“Gauge” means pressure added above the surrounding atmosphere; “absolute” includes
atmospheric pressure.

| Added pressure, gauge | Absolute pressure | Illustrative core-radius cutoff | Potential extra contraction factor | Potential extra similarity-time decades | Estimated pressure-system addition |
|---:|---:|---:|---:|---:|---:|
| 0 bar | 1.01 bar | 73.4 µm | 1× | 0 | $0 |
| +1 bar, about 14.5 psi | 2.01 bar | 51.8 µm | 1.42× | 0.30 | **+$15k–40k** |
| +4 bar, about 58 psi | 5.01 bar | 32.7 µm | 2.25× | 0.70 | **+$30k–90k** |
| +9 bar, about 131 psi | 10.01 bar | 23.1 µm | 3.18× | 1.00 | **+$60k–180k** |

The extra factors compare each pressure with the atmospheric cavitation threshold;
they do not multiply the demonstrated range of a real apparatus. Extra
similarity-time decades additionally assume the square-root scaling.

The pressure-package allowances are particularly uncertain, unquoted design
estimates for a roughly 6 L, 20 cm-scale apparatus with multiple useful optical
views and many fluid connections. They include replacement pressure-containing
hardware, windows/seals, pressure regulation and relief, compatible loop and
sensor changes, mechanical design/testing services and contingency. They do
not include a new high-end imaging system or the flow research labor. A small
pressure cell with one tiny viewing port can be much cheaper and is not an
equivalent apparatus. These are total additions for each pressure option,
not steps to sum. A retrofit could discard more equipment than a planned build.

Apply approximately the **same pressure-package addition to either ownership
route** unless the shared lab already has a suitable pressure-rated optical
vessel and compatible loop. Ordinary shared cameras do not eliminate the custom
vessel cost. For example, combining the ambitious atmospheric row with the
+4 bar option gives approximately **$110k–340k from scratch**, or
**$70k–240k additional equipment in an otherwise equipped lab**. It does not
establish an improvement over a 1 mm delivery/optics limit.

I found no public quote for our multi-window vessel. The manufacturer
[Parr's optical-window description](https://www.parrinst.com/products/stirred-reactors/options-accessories/windows/)
confirms that aperture, mounting, pressure rating and custom geometry are linked;
it does not supply the dollar allowances above. Preserving wide optical access
is a major reason an ordinary pressure container's price is a poor comparison.
The pressure-rated assembly needs its own engineered design; this budget does
not authorize pressurizing the illustrative transparent tank.

Obtaining ten times smaller radius **solely by postponing cavitation** would
need about 100 times the atmospheric pressure margin—approximately **99 bar
absolute** in this illustration. This would add two conditional similarity-time
decades only if every other limit had been overcome. It is not a proposed or
costed design.

Pressurization does not amplify a tiny differential-pressure signal; measuring
that signal under high background pressure can become harder. In a balanced
pressurized recirculation loop, pump hydraulic power mainly depends on flow
multiplied by pressure losses, rather than flow multiplied by background absolute
pressure. Containment and optical integration can dominate the added cost.

### Assumptions behind the pressure table

For reproducibility, the model uses water at 20 °C, density rho=998.2 kg/m³,
vapor pressure p_v=2340 Pa and atmospheric pressure p_atm=101325 Pa. Gaussian
width b and peak speed U satisfy U b=0.0005 m²/s; the swirl-induced pressure drop
is 1.702 rho U². The measured peak radius r is 1.1209 b. With pressures in pascals:

```text
b_cav = 0.0005 * sqrt(1.702 rho / (p_abs - p_v))
r_cav = 1.1209 b_cav
extra contraction factor = sqrt[(p_abs - p_v)/(p_atm - p_v)]
extra similarity-time decades = log10[(p_abs - p_v)/(p_atm - p_v)]
```

The corresponding Gaussian widths are 65.5, 46.2, 29.2 and 20.6 µm. Expressing
the table as peak radii changes the length convention, not the pressure model
or the extension factors. Heating, gas nuclei, other velocity components and
finite-vessel geometry can shift the actual cavitation threshold.

## Labor, shared facilities and recurring costs

A usable cash estimate is:

```text
new equipment + chosen pressure upgrade + hired research labor
+ facility charges + taxes/shipping/other applicable overhead.
```

Count each item once. The atmospheric budget rows are alternatives; each pressure
addition is also an alternative. If equipment can be reused during an upgrade,
subtract only the purchases it actually replaces.

As an explicit labor-planning scenario, allow **200–800 hours** of owner/research effort for the
modest apparatus through initial calibration and experiments. If bought at an
assumed **$75–150/hour**, that adds **$15k–120k**. For the quantitative mechanism
or 1 mm program, **1,000–3,000 hours** adds **$75k–450k** at the same assumed
rates. These are my workload/rate assumptions, not quotes or completion-time
promises; unsuccessful iterations can exceed them. They exclude fabrication
or mechanical design already bought in the equipment/pressure package to avoid
double counting. Personal time or salaried lab staff reduces the new cash bill,
not the effort required.

There is a real pay-for-access alternative. The University of Cincinnati's
micro-PIV facility lists **$60/hour external equipment use plus $100/hour staff
time**, with lower internal rates. Twenty equipment hours with ten staff hours
would be $2,200 at those posted rates. This illustrates shared-facility billing; it does not establish that a
microscope micro-PIV setup can accept our tank or supply its three-dimensional
measurements. Relevant tank-scale PIV/PTV access,
setup time and permission to install a custom loop require a separate agreement.
[Facility description and rates](https://www.ceas.uc.edu/research/centers-labs/clean-room/equipment.html).

As a budgeting placeholder, reserve **$1k–5k per active year** for a small
atmospheric apparatus's tracer/filter/tubing/seal replacements, reference checks,
data storage and modest maintenance. An extensive laser/multi-channel facility
may need **$5k–20k+**, before software renewals, paid access, staffing or major
repairs. These are allowances, not service contracts. The cost of the water
itself is negligible compared with instrumentation and development.

## Recommended spending sequence

1. **Test feasibility at atmospheric pressure:** $3k–8k from scratch or $1k–4k
   with suitable lab resources. Establish a reproducible core, useful boundary
   response and calibrated pressure/velocity measurements.
2. **Pursue the modest contraction:** approximately $12k–35k or $5k–18k total
   equipment for that capability. Aim at 10→3 mm. Reuse the feasibility equipment
   where suitable; do not simply add the two budgets.
3. **Choose the next scientific question:** invest in complete 3D momentum
   accounting to test the perturbation mechanism, or in delivery and imaging
   that might extend contraction toward 1 mm. Neither result guarantees the other.
4. **Consider pressure only after measuring a pressure-related limit.** Better
   optics, calibrated actuation and temperature control are more likely to help
   while the smallest attainable core remains millimetre-scale.

Shared or borrowed suitable imaging equipment could save more than simplifying
the tank. A larger physical scale can also ease optical resolution, although
flow demands and vessel cost must be recalculated. Slower schedules or lower
circulation are alternatives to pressure only if they preserve the intended
viscous and perturbation dynamics.

The proposed next design document is a bill of materials for the small atmospheric
feasibility bench: what must be measured, which items are owned or borrowable,
what needs purchasing, and what result would justify expansion. No purchases
or implementation have been started; the
[handoff](../../SESSION_HANDOFF.md#next-task) retains the execution pause.
