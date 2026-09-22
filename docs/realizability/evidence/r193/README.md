# R193 retained analytical checks

[Decision sheet](../../INWARD_TRANSPORT_SCREEN_R193.md).
Run from the repository with:

```bash
.venv/bin/python docs/realizability/evidence/r193/check_transport.py
```

Python 3.12.14, standard library only. The command regenerates
[transport_screen.json](transport_screen.json) next to
[check_transport.py](check_transport.py). Fifteen groups passed: characteristic
roots/PDE residuals, Stokes and inviscid limits, sign/conjugacy, geometry,
independent real-root attenuation, cylindrical angular-momentum diffusion
transform, standing-wave decomposition, conditional strain path/exit,
phase cancellation, scalar residual bound and gain-threshold identities.
The threshold search evaluates a closed-form expression; it is not a PDE solve.

The JSON records full-precision comparison gains, geometry, local conditional
swirl, timing and turnover scales. All inputs are the R192 design assumptions
or explicitly artificial constant path speeds/coefficient choices. No actual
base, streamline, boundary-to-core gain, error floor or hardware capability is
measured or validated. No field sampling, CFD/FEM or physical run occurred.
