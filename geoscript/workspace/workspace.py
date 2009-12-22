"""
workspace module -- Provides data access and manipulation of collections of 
layers.
"""

from geoscript.layer import Layer
from geoscript import geom, feature

class Workspace:
  """
  A workspace is a collection of layers.
  """

  def __init__(self, ds=None):
    if self.__class__ == Workspace and not ds:
      import memory
      mem = memory.MemoryWorkspace()
      self.ds = mem.ds
    else :
      if not ds:
        raise Exception('Worksapce requires a data store.')

      self.ds = ds

  def layers(self):
    """
    The names of all the layers in the workspace.

    >>> ws = Workspace()
    >>> l1 = ws.newLayer('foo')
    >>> l2 = ws.newLayer('bar')
    >>> ws.layers()
    ['foo', 'bar']
    """

    return [str(tn) for tn in self.ds.typeNames]

  def layer(self,name):
    """
    Returns a layer in the workspace.

    >>> ws = Workspace()
    >>> l = ws.layer('foo')
    >>> str(l)
    'None'
    >>> x = ws.newLayer('foo')
    >>> l = ws.layer('foo') 
    >>> str(l.name)
    'foo'

    This method returns None if no such layer is defined.
    """

    if name in self.layers():
       fs = self.ds.getFeatureSource(name)
       return Layer(fs)
  
    return None

  def newLayer(self, name, flds=[('geom', geom.Geometry)]):
     """
     Creates a new layer in the workspace.
   
     >>> from geoscript import geom
     >>> ws = Workspace()
     >>> l = ws.newLayer('foo', [('geom', geom.Point)])
     >>> ws.layers()
     ['foo']
     """

     if self.layer(name):
       raise Exception('Layer %s already exists.' % (name))

     schema = feature.Schema(name, flds)
     self.ds.createSchema(schema.ft) 
     return self.layer(name)

  def addLayer(self, layer, name=None):
     """
     Adds an existing layer to the workspace.
    
     >>> ws = Workspace()
     >>> ws.layers()
     []
     >>> from geoscript.feature import Schema
     >>> from geoscript.layer import MemoryLayer
     >>> l = MemoryLayer(name='foo')
     >>> l = ws.addLayer(l)
     >>> ws.layers()
     ['foo']
     """

     name = name if name else layer.name
     l = self.layer(name)
     if not l:
       if layer.proj:
         flds = []
         for fld in layer.schema.fields:
           flds.append((fld.name, fld.typ, layer.proj) if issubclass(fld.typ, geom.Geometry) else (fld.name, fld.typ))
       else:
         flds = [(fld.name, fld.typ) for fld in layer.schema.fields]
       l = self.newLayer(name, flds)
     
     for f in layer.features():
       l.add(f)

     return l
