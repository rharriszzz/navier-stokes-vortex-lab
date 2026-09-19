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
    pigment { color rgb <0.10, 0.78, 0.95> }
    finish {
      diffuse 0.45
      phong 0.85
      phong_size 50
      reflection 0.04
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
    pigment { color rgb <0.85, 0.08, 0.06> }
    finish { phong 0.45 }
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
