// actuators.inc
// Illustrative diaphragm housings, support rings, and pressure sensor markers.

#declare NActuatorsPerRing = 16;
#declare NSensorsPerRing = 8;

// Shared housing faces inward along -x before rotation around the tank axis.
#declare ActuatorHousing = union {
  cylinder {
    <0.88, 0, 0>, <0.94, 0, 0>, 0.044
    material { ActuatorMaterial }
  }
  torus {
    0.035, 0.006
    rotate z*90
    translate x*0.88
    material { DiaphragmMaterial }
  }
}

#macro RenderActuatorRing(ZRing, PhaseOffset)
  torus {
    0.925, 0.009
    rotate x*90
    translate z*ZRing
    material { ActuatorMaterial }
  }
  #local I = 0;
  #while (I < NActuatorsPerRing)
    #local Theta = 2*pi*I/NActuatorsPerRing;
    // Zero-mean m=4 command; exaggerated bulging about a preloaded face.
    // This illustrates motion, not a fluid-structure or volume-flux solution.
    #local Command = cos(4*Theta + ActuatorPhase + PhaseOffset);
    #local Bulge = 0.012 + 0.010*Command;
    union {
      object { ActuatorHousing }
      sphere {
        <0, 0, 0>, 1
        scale <Bulge, 0.030, 0.030>
        translate x*0.88
        material { DiaphragmMaterial }
      }
      rotate z*degrees(Theta)
      translate z*ZRing
    }

    #local I = I + 1;
  #end
#end

#macro RenderSensorRing(ZRing)
  #local I = 0;
  #while (I < NSensorsPerRing)
    // Offset sensors between housings and keep all hardware inside the tank.
    #local Theta = 2*pi*I/NSensorsPerRing + pi/NActuatorsPerRing;
    #local P = <0.945*cos(Theta), 0.945*sin(Theta), ZRing>;

    sphere {
      P, 0.018
      material { SensorMaterial }
    }

    #local I = I + 1;
  #end
#end

#macro RenderActuatorsAndSensors()
  // Four posts support the rings from the tank floor.
  #local I = 0;
  #while (I < 4)
    #local Theta = pi/4 + I*pi/2;
    #local P = <0.925*cos(Theta), 0.925*sin(Theta), 0>;
    cylinder {
      P + z*(-TankHalfZ + TankWall), P + z*0.56, 0.009
      material { ActuatorMaterial }
    }
    #local I = I + 1;
  #end
  RenderActuatorRing(-0.55, -0.7)
  RenderActuatorRing( 0.00,  0.0)
  RenderActuatorRing( 0.55,  0.7)

  RenderSensorRing(-0.80)
  RenderSensorRing( 0.00)
  RenderSensorRing( 0.80)
#end
