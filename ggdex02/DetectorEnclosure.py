import sys
import gegede.builder
from gegede import Quantity as Q

class Builder(gegede.builder.Builder):
    '''
    Build the detector enclosure with several layers.
       material -- The material used to build the detector enclosure.
       subbuilders -- A list of builders for the layers of the enclosures.
       repetitions -- The number of repetions of the stack of layers.
       dx, dy, dz -- The half size of the world box.

       Remaining configuration parameters are added to the logical
       volume as <auxilliary auxtype="key" auxvalue="value" /> pairs.
    '''

    def configure(self,
                  material = "Air",
                  dx = Q("1m"),
                  dy = Q("1m"),
                  dz = Q("1m"),
                  repetitions = 1,
                  **kwds):
        print("Configuring the detector enclosure " + self.name)
        self.material = material
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.repetitions = repetitions
        self.otherKeywords = kwds
        pass

    def construct(self, geom):
        print("Constructing the detector enclosure " + self.name)

        ## Build the volume for this layer.  The conventions are that
        ## the shape name ends in "_shape", and the volume name ends
        ## in "_LV".  This reflects what is going to be build in
        ## GEANT4 (a G4Shape and a G4LogicalVolume).
        ##
        ## The shape and volume names need to be unique inside the
        ## GDML file.
        shape = geom.shapes.Box(self.name + "_shape",
                                self.dx, self.dy, self.dz)
        volume = geom.structure.Volume(self.name + "_LV",
                                       material = self.material,
                                       shape = shape)

        ## Add the constructed volume to the builder.  This can be
        ## added before the volume is fully constructed.
        self.add_volume(volume)

        ## Add the aux type and aux values fields to the logical volume.
        for n, v in self.otherKeywords.items():
            volume.params.append((n,v))
            pass

        ####################################################
        ## Add a stack of layers to the parent volume.
        ####################################################

        subBuilders = self.get_builders()

        ## Determine the full size of the stack of layers
        halfX = Q("0m")
        halfY = Q("0m")
        halfZ = Q("0m")
        for rep in range(self.repetitions):
            for subBuilder in subBuilders:
                halfX = max(halfX,subBuilder.dx)
                halfY = max(halfX,subBuilder.dx)
                halfZ += subBuilder.dz

        ## Make sure the parent volume is big enough.
        if self.dx < halfX or self.dy < halfY or self.dz < halfZ:
            raise RuntimeError("invalid geometry in " + self.name
                               + " -- Must satisfy"
                               + " " + str(halfX) + " < " + str(self.dx) 
                               + " AND " + str(halfY) + " < " + str(self.dy) 
                               + " AND " + str(halfZ) + " < " + str(self.dz))

        ## Place the sub volumes in the parent volume.  The
        ## coordinates are relative to the parent volume.
        centerX = Q("0m")
        centerY = Q("0m")
        centerZ = - halfZ
        for rep in range(self.repetitions):
            for subBuilder in subBuilders:
                centerZ += subBuilder.dz
                vol = subBuilder.get_volume()
                pos = geom.structure.Position(subBuilder.name+"_pos"+str(rep),
                                              centerX, centerY, centerZ)
                rot = geom.structure.Rotation(subBuilder.name+"_rot"+str(rep),
                                              "0deg","0deg","0deg")
                place = geom.structure.Placement(
                    subBuilder.name+"_place"+str(rep),
                    volume=vol.name,
                    pos=pos.name,
                    rot=rot.name)
                volume.placements.append(place.name)
                centerZ += subBuilder.dz
                pass
            pass
        pass
