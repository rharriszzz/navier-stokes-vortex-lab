// tracer.inc
// Shared tracer bead prototype and rendering macro.

#ifndef (TracerRadius)
  // Exaggerated visual marker size, not the physical PIV particle radius.
  // Changing this does not affect passive-tracer trajectories.
  #declare TracerRadius = 0.014;
#end

#declare TracerPrototype =
sphere {
  <0, 0, 0>, TracerRadius
  material { TracerMaterial }
  // Magnified markers should not cast macroscopic bead shadows.
  no_shadow
}

#macro RenderTracers()
  #local I = 0;
  #while (I < NBeads)
    object {
      TracerPrototype
      translate BeadPos[I]
    }
    #local I = I + 1;
  #end
#end
