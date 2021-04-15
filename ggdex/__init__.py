#!/usr/bin/env python
'''An example GeGeDe module.

This provides some builder classes to build a Rubik's cube.

Warning: any resemblance between the result and an actual Rubik's cube
is purely accidental.  It's really just a 3x3x3 stack of blocks less
one at the origin.
'''

import gegede.builder
from gegede import Quantity as Q

class WorldBuilder(gegede.builder.Builder):
    '''
    Build a simple box world of given material and size.
    '''
    def configure(self, material = 'Air', size = Q("1m"), **kwds):
        print ("Configure WorldBuilder for " + self.name)
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        print ("Construct WorldBuilder volume for " + self.name)
        ## Define the materials.  All materials should be defined in
        ## the world builder construct method.
        h = geom.matter.Element("Elem_hydrogen", "H", 1, "1.00791*g/mole" )
        c = geom.matter.Element("Elem_carbon",   "C", 6, "12.0107*g/mole")
        n = geom.matter.Element("Elem_nitrogen", "N", 7, "14.0671*g/mole")
        o = geom.matter.Element("Elem_oxygen",   "O", 8, "15.999*g/mole" )
        plastic = geom.matter.Mixture("Plastic",   density="1.05*g/cc",
                                      components = (
                                          ("Elem_carbon",   0.9),
                                          ("Elem_hydrogen", 0.1)
                                      ))
        air = geom.matter.Mixture("Air",
                                  density = "0.001225*g/cc",
                                  components = (
                                      ("Elem_nitrogen", 0.8),
                                      ("Elem_oxygen",   0.2),
                                  ))
        
        ## Build the volume
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)

        volume = geom.structure.Volume(self.name+'_volume', 
                                   material=self.material, shape=shape)

        subBuilder = self.get_builder()
        subVolume = subBuilder.get_volume()
        place = geom.structure.Placement(subBuilder.name + "_place",
                                         volume=subVolume.name)

        volume.placements.append(place.name)                

        self.add_volume(volume)

class RubikBuilder(gegede.builder.Builder):
    '''Build a Rubik's cube (kind of).  

    Delegate to three sub-builders assumed to provide each one of, in
    order, corner, edge and center blocks.  Blocks are assumed to be
    cubes of equal size.

    '''

    def configure(self, material = 'Air', gap = Q("1mm"), **kwds):
        print ("Configure RubikBuilder for " + self.name)
        self.material, self.gap = (material, gap)
        pass

    def construct(self, geom):
        print ("Construct RubikBuilder volume for " + self.name)

        # get volumes from sub-builders.  Note, implicitly assume
        # order, which must be born out by configuration.  Once could
        # remove this by querying each sub-builder for its "location"
        # configuration parameter, but this then requires other
        # assumptions.
        blocks = [sb.get_volume() for sb in self.get_builders()]
        block_shape = geom.store.shapes.get(blocks[-1].shape)
        
        blocks.reverse()        # you'll see why

        # Calculate overall dimensions from daughters.  Assume identical cubes!
        half_size = (block_shape.dx + self.gap) * 3
        dim = (half_size,)*3

        # make overall shape and LV
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        volume = geom.structure.Volume(self.name+'_volume', 
                                   material=self.material, shape=shape)
        self.add_volume(volume)
        
        # distance between two adjacent blocks
        step = (block_shape.dx + self.gap)*2

        # place daughter LV
        for ii in [-1,0,1]:         # x
            for jj in [-1,0,1]:     # y
                for kk in [-1,0,1]: # z
                    trip = (ii,jj,kk)
                    if trip == (0,0,0):
                        continue

                    which = sum([abs(x) for x in trip]) - 1
                    lv = blocks[which] # that's why

                    trip_name = '%d%d%d' % trip
                    pos = geom.structure.Position('pos_'+trip_name,
                                                  x=ii*step,y=jj*step,z=kk*step)
                    place = geom.structure.Placement("place_" +trip_name,
                                                     volume=lv, pos=pos)
                    volume.placements.append(place.name)                
                    continue
                continue
            continue
        return

class RubikBlockBuilder(gegede.builder.Builder):
    '''
    Build a corner, edge or center Rubik's cube block.
    '''
    def configure(self, location = "center", material = 'Plastic', size = Q("1cm"), **kwds):
        print ("Configure RubikBlockBuilder for " + self.name)
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        print ("Construct RubikBlockBuilder volume for " + self.name)
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', 
                                   material=self.material, shape=shape)
        self.add_volume(lv)
