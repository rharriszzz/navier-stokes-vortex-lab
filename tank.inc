// tank.inc
// Transparent outer tank plus subtle internal PIV light sheet.

#declare TankHalfX = 1.00;
#declare TankHalfY = 1.00;
#declare TankHalfZ = 1.15;
#declare TankWall = 0.035;

#macro RenderTank()
  difference {
    box {
      <-TankHalfX, -TankHalfY, -TankHalfZ>,
      < TankHalfX,  TankHalfY,  TankHalfZ>
    }
    box {
      <-TankHalfX + TankWall, -TankHalfY + TankWall, -TankHalfZ + TankWall>,
      < TankHalfX - TankWall,  TankHalfY - TankWall,  TankHalfZ - TankWall>
    }
    material { TankGlassMaterial }
    hollow
  }

  // PIV sheet: y ~= 0.
  #if (ShowPIVSheet)
    box {
      <-0.90, -0.003, -0.98>,
      < 0.90,  0.003,  0.98>
      material { PIVMaterial }
      no_shadow
    }
  #end
#end

#macro RenderCore()
  cylinder {
    <0, 0, -CoreHalfHeight>,
    <0, 0,  CoreHalfHeight>,
    CoreRadius
    material { CoreMaterial }
    no_shadow
  }
#end
