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
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)

        lv = geom.structure.Volume(self.name+'_volume', 
                                   material=self.material, shape=shape)
        self.add_volume(lv)

class RubikBuilder(gegede.builder.Builder):
    '''Build a Rubik's cube (kind of).  

    Delegate to three sub-builders assumed to provide each one of, in
    order, corner, edge and center blocks.  Blocks are assumed to be
    cubes of equal size.

    '''

    def configure(self, material = 'Air', gap = Q("1mm"), **kwds):
        self.material, self.gap = (material, gap)
        pass

    def construct(self, geom):

        # get volumes from sub-builders.  Note, implicitly assume
        # order, which must be born out by configuration.  Once could
        # remove this by querying each sub-builder for its "location"
        # configuration parameter, but this then requires other
        # assumptions.
        corner, edge, center = blocks = [sb.volumes[0] for sb in self.builders]
        block_lv = geom.store.structure.get(center)
        block_shape = geom.store.shapes.get(block_lv.shape)

        blocks.reverse()        # you'll see why

        # Calculate overall dimensions from daughters.  Assume identical cubes!
        half_size = (block_shape.dx + self.gap) * 3
        dim = (half_size,)*3

        # make overall shape and LV
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', 
                                   material=self.material, shape=shape)
        self.add_volume(lv)
        
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
                    geom.structure.Placement("place_" +trip_name,
                                             volume=lv, pos=pos)
                    continue
                continue
            continue
        return

class RubikBlockBuilder(gegede.builder.Builder):
    '''
    Build a corner, edge or center Rubik's cube block.
    '''
    def configure(self, location = "center", material = 'Plastic', size = Q("1cm"), **kwds):
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', 
                                   material=self.material, shape=shape)
        self.add_volume(lv)
