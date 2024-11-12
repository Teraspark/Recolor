#!/bin/env python3

#Constants
RED = 0
GREEN = 1
BLUE = 2
R, G, B = 0, 1, 2

def TOGBA(v):
  '''convert from true color to 15bit gba color'''
  return v >> 3

def FROMGBA(v):
  '''convert from 15bit gba color to true color (estimate)'''
  return (v << 3) | (v >> 2)

class Color:
  '''Represents the RGB values of a color'''
  def __init__(self, red = 0, green = 0, blue = 0):
    self.r = red
    self.g = green
    self.b = blue
  
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.flatten() == other.flatten()
    elif isinstance(other, (tuple, list)):
      return self.flatten() == tuple(other)
    return False
  
  # def is_color(self,red,green,blue):
    # '''check if object holds the given color'''
    # if self.r == red and \
      # self.g == green and \
      # self.b == blue:
      # return True
    # else:
      # return False
  
  # def same(c):
    # '''check if the color objects hold the same color'''
    # if type(c) is Color:
      # if self.r == c.r and \
        # self.g == c.g and \
        # self.b == c.b:
        # return True
    # return False
  
  def to_gba_hex(self, tc = False):
    r = TOGBA(self.r) if tc else self.r
    g = TOGBA(self.g) if tc else self.g
    b = TOGBA(self.b) if tc else self.b
    
    r = r & 0x1f
    g = (g & 0x1f) << 5
    b = (b & 0x1f) << 10
    h = hex(b|g|r).removeprefix('0x')
    
    # add leading 0s if necessary
    if len(h) % 4: h = '0'*(4 - len(h) % 4) + h
    b = bytearray.fromhex(h)
    b.reverse()
    return b.hex()
  
  @classmethod
  def from_gba_hex(cls, h, tc = False):
    '''convert palette from hex string to object
    set tc to True if converting to true color'''
    
    # remove all whitespace from string
    h = ''.join(h.split())
    if len(h) != 4:
      raise ValueError('hexstring is invalid size')
    b = bytearray.fromhex(h)
    b.reverse()
    v = int(b.hex(), 16)
    r = v & 0x1f
    g = (v >> 5) & 0x1f
    b = (v >> 10) & 0x1f
    if(tc):
      r = FROMGBA(r)
      g = FROMGBA(g)
      b = FROMGBA(b)
    return Color(r,g,b)
    
  def flatten(self):
    '''return rgb as tuple'''
    return (self.r,self.g,self.b)

class Palette:
  '''colorlist is an array of Color class objects'''
  colors = ()
  def __init__(self, flat=(), length = 0, colorlist = None):
    '''
    flat: 1d tuple for all rgb values
    
    
    length: amount of colors in the palette
    '''
    if colorlist:
      self.colors = colorlist
    elif flat:
      flat = tuple(flat)
      f = len(flat)
      if f % 3:
        raise ValueError('invalid flat palette length')
      for x in range(0,f,3):
        self.colors += (
          Color(flat[x],flat[x + 1], flat[x + 2]),)
    elif length:
      for c in range(length):
        self.colors += (Color(),)
    
  def __eq__(self, other):
    if isinstance(other,self.__class__):
      return self.flatten() == other.flatten()
    elif isinstance(other, (tuple, list)):
      return self.flatten() == tuple(other)
    return False
  
  def __len__(self):
    return len(self.colors)
  
  def new_color(self, c):
    '''add new color to palette'''
    self.colors+= (Color(c[R],c[G],c[B]),)
    return len(self.colors)-1
    
  def edit_color(self, i, c):
    '''edit existing color in palette'''
    # if 0 < i < len(self.colors):
    if isinstance(c, Color): c = c.flatten()
    self.colors[i].r = c[RED]
    self.colors[i].g = c[GREEN]
    self.colors[i].b = c[BLUE]
    
  def get_color(self, i):
    return self.colors[i]
  
  def find_color(self, cx):
    '''return index of color in Palette
      return -1 if i not in Palette'''
    s = len(self.colors)
    for c in range(s):
      if self.colors[c] == cx:
        return c
    return -1
    
  def to_gba_hex(self, tc = False):
    '''convert palette into a hexstring'''
    h = ""
    for c in self.colors:
      h += c.to_gba_hex(tc)
    return h
  
  def to_data(self):
    d = []
    for c in self.colors:
      z = {}
      (r,g,b) = c.flatten()
      z["red"] = r
      z["green"] = g
      z["blue"] = b
      d.append(z)
    return d
  
  @classmethod
  def from_gba_hex(cls, h, tc = False):
    h = ''.join(h.split()) # remove all whitespace
    if len(h) % 4:
      raise ValueError(
        'hex string is invalid length')
    s = len(h)
    p = ()
    for b in range(0, s, 4):
      c = h[b : b + 4]
      p += (Color.from_gba_hex(c, tc),)
    return Palette(colorlist = p)
  
  @classmethod
  def from_data(cls, data):
    # # sort if all colors are indexed
    # if all('index' in d for d in data):
      # data.sort(key = lambda c: c.index)
    p = ()
    for c in data:
      r = 0 if 'red' not in c else c['red']
      g = 0 if 'green' not in c else c['green']
      b = 0 if 'blue' not in c else c['blue']
      p += (Color(r, g, b),)
    return Palette(colorlist = p)
    
  def flatten(self):
    '''return palette as a tuple'''
    flatpal = ()
    for c in self.colors:
      flatpal += c.flatten()
    return flatpal
    
'''
def rgbtohex(r,g,b):
  h = hex((b&0x1f)<<10 | (g&0x1f) << 5 | r&0x1f).removeprefix('0x')
  b = bytearray.fromhex(h)
  b.reverse()
  return b.hex()
def hextorgb(hstr):
  b = bytearray.fromhex(hstr)
  b.reverse()
  print(b)
  v = int(b.hex(),16)
  print(v)
  r = v & 0x1f
  g = (v >> 5) & 0x1f
  b = (v >> 10) & 0x1f
  print(r,g,b)
  return (r,g,b)
  
convert from 15bit to true color (estimate)
  (b<<3)|(b>>2)
convert from true color to 15bit
  c >> 3
  
  
for y in range(z.height):
  for x in range(z.width):
    c = y.getpixel((x,y))
    r,g,b = c[0],c[1],c[2]
    if (r,g,b) not in p:

'''