// tracer.inc
// Shared tracer bead prototype and rendering macro.

#ifndef (TracerRadius)
  #declare TracerRadius = 0.018;
#end

#declare TracerPrototype =
sphere {
  <0, 0, 0>, TracerRadius
  material { TracerMaterial }
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
