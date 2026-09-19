// materials.inc
// Shared materials for navier-stokes-vortex-lab.

#declare TankGlassMaterial =
material {
  texture {
    pigment { color rgbf <0.82, 0.92, 1.00, 0.90> }
    finish {
      diffuse 0.10
      specular 0.75
      roughness 0.008
      reflection 0.04
      conserve_energy
    }
  }
  interior { ior 1.50 }
}

#declare TracerMaterial =
material {
  texture {
    // Illustrative fluorescent seeding particles under illumination.
    // Emission is a visibility aid, not a simulation of laser excitation.
    pigment { color rgb <0.08, 1.00, 0.65> }
    finish {
      ambient 0
      emission 0.55
      diffuse 0.35
      specular 0.08
      roughness 0.08
    }
  }
}

#declare CoreMaterial =
material {
  texture {
    pigment { color rgbf <1.00, 0.30, 0.05, 0.58> }
    finish {
      diffuse 0.55
      specular 0.25
    }
  }
}

#declare ActuatorMaterial =
material {
  texture {
    pigment { color rgb <0.38, 0.41, 0.44> }
    finish { diffuse 0.65 specular 0.25 roughness 0.06 }
  }
}

#declare DiaphragmMaterial =
material {
  texture {
    pigment { color rgb <0.07, 0.08, 0.09> }
    finish { diffuse 0.70 specular 0.12 roughness 0.10 }
  }
}

#declare SensorMaterial =
material {
  texture {
    pigment { color rgb <0.05, 0.20, 0.85> }
    finish { phong 0.55 }
  }
}

#declare PIVMaterial =
material {
  texture {
    pigment { color rgbf <0.10, 1.00, 0.30, 0.84> }
    finish {
      diffuse 0.10
      emission 0.18
    }
  }
}
