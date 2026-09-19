// actuators.inc
// Three circumferential actuator rings and pressure sensor markers.

#declare NActuatorsPerRing = 16;
#declare NSensorsPerRing = 8;

#macro Arrow(StartPoint, Direction, Length, ShaftRadius, HeadRadius)
  #local DirLen = vlength(Direction);
  #if (DirLen > 1e-8)
    #local UnitDir = Direction / DirLen;
    #local Tip = StartPoint + UnitDir * Length;
    #local ShaftEnd = StartPoint + UnitDir * (Length * 0.72);

    cylinder {
      StartPoint,
      ShaftEnd,
      ShaftRadius
      material { ActuatorMaterial }
    }

    cone {
      ShaftEnd, HeadRadius,
      Tip, 0
      material { ActuatorMaterial }
    }
  #end
#end

#macro RenderActuatorRing(ZRing, PhaseOffset)
  #local I = 0;
  #while (I < NActuatorsPerRing)
    #local Theta = 2*pi*I/NActuatorsPerRing;
    #local P = <cos(Theta), sin(Theta), ZRing>;
    #local RadialIn = <-cos(Theta), -sin(Theta), 0>;

    // m=4 command. Sign changes arrow direction.
    #local Command = 0.5 + 0.5*cos(4*Theta + ActuatorPhase + PhaseOffset);
    #local Length = 0.035 + 0.12*Command;

    sphere {
      P, 0.022
      material { ActuatorMaterial }
    }

    Arrow(P, RadialIn, Length, 0.009, 0.022)

    #local I = I + 1;
  #end
#end

#macro RenderSensorRing(ZRing)
  #local I = 0;
  #while (I < NSensorsPerRing)
    #local Theta = 2*pi*I/NSensorsPerRing;
    #local P = <1.025*cos(Theta), 1.025*sin(Theta), ZRing>;

    sphere {
      P, 0.018
      material { SensorMaterial }
    }

    #local I = I + 1;
  #end
#end

#macro RenderActuatorsAndSensors()
  RenderActuatorRing(-0.55, -0.7)
  RenderActuatorRing( 0.00,  0.0)
  RenderActuatorRing( 0.55,  0.7)

  RenderSensorRing(-0.80)
  RenderSensorRing( 0.00)
  RenderSensorRing( 0.80)
#end
