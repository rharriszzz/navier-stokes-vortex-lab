// fluid.pov
// Main POV-Ray scene for navier-stokes-vortex-lab.
//
// The numerical trajectory integration is performed by make_trajectories.py.
// This file selects the include file corresponding to the current POV-Ray
// animation frame and renders the geometry.

#version 3.7;

// Optional explanatory overlays; hide them for tracer-motion tests.
#ifndef (ShowPIVSheet)
  #declare ShowPIVSheet = false;
#end
#ifndef (ShowCore)
  #declare ShowCore = false;
#end
#ifndef (ShowActuators)
  #declare ShowActuators = false;
#end
#ifndef (ShowSensors)
  #declare ShowSensors = true;
#end

#include "colors.inc"
#include "materials.inc"
#include "tank.inc"
#include "actuators.inc"
#include "tracer.inc"

global_settings {
  assumed_gamma 1.0
  max_trace_level 12
}

background { color rgb <0.97, 0.98, 1.00> }

// POV-Ray animation frames are conventionally 1-based here.
#declare FrameIndex = frame_number;

#declare PositionFile =
  concat(
    "positions/frame",
    str(FrameIndex, -4, 0),
    ".inc"
  );

#include PositionFile

camera {
  perspective
  location <3.35, -4.65, 2.85>
  look_at <0, 0, 0>
  sky <0, 0, 1>
  angle 34
}

light_source {
  <4.0, -5.5, 7.0>
  color rgb <1.0, 0.96, 0.90> * 1.25
  area_light <1.5,0,0>, <0,1.5,0>, 5, 5
  adaptive 1
  // No area-light jitter: avoid frame-to-frame shadow noise in animation.
}

light_source {
  <-4.0, -2.0, 3.0>
  color rgb <0.55, 0.65, 1.0> * 0.55
}

light_source {
  <0.0, 4.0, 2.0>
  color rgb <1.0, 1.0, 1.0> * 0.45
}

plane {
  z, -1.25
  pigment { color rgb <0.86, 0.87, 0.90> }
  finish { diffuse 0.80 }
}

RenderTank()
#if (ShowCore)
  RenderCore()
#end
#if (ShowActuators)
  RenderActuators()
#end
#if (ShowSensors)
  RenderSensors()
#end
RenderTracers()
