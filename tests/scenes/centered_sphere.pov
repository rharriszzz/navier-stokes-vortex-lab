#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb <0.97, 0.98, 1.00> }
camera {
  perspective
  location <0, 0, -3>
  look_at <0, 0, 0>
  angle 45
}
light_source { <-2, -3, -4> color rgb 1 }
sphere {
  <0, 0, 0>, 0.75
  pigment { color rgb <1, 0, 0> }
  finish { diffuse 0.8 }
}
