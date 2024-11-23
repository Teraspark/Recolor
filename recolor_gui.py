# import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
import xml.etree.ElementTree as ET

import tkextras as tkx
from PIL import Image,ImageTk
import palette as PD

# File loading/saving functions
def askForFileIn(filedata=()):
	filedata += (("all files","*.*"),)
	file = askopenfilename(title="Open",filetypes=filedata)
	return Path(file)

def askForFileOut(filedata=()):
	filedata += (("all files","*.*"),)
	file = asksaveasfilename(title="Save As",filetypes=filedata)
	return Path(file)

def isValidFile(file):
	if not file:
		return False
	return file.is_file()

def ishex(h):
  '''check if h is valid hexadecimal'''
  s1 = set(h.lower().removeprefix('0x'))
  s2 = set('0123456789abcdef')
  if s1 <= s2:
    return True
  else:
    return False

class Palstruct():
  gin = 0 # current group index
  data = {}
  
  # TODO
  # - Add iterator
  # - load/save file
  # - switch group
  # - delete group
  
  def __init__(self):
    self.data['palg'] = [{}]
    self.data['palg']["color"] = []
  
  def savetoml(self,filepath):
    '''load info from toml file'''
    pass
  
  def loadtoml(self,filepath):
    '''save info into toml file'''
    pass
  
  def newgroup(self):
    self.data['palg'].append({})
    g = self.data['palg'][-1]
    g['palette'] = {}
    
  def curgroup(self):
    return self.data['palg'][gin]

class Colorbox(tk.Frame):
  '''set of widgets made for the rgb section'''
  def __init__(self, parent, src, id, update = None, *args, **kwargs):
    '''
    :param parent: parent widget
    :param src: source color (tuple)
    :param id: int color number in palette
    '''
    super().__init__(parent, *args, **kwargs)
    self.ocrgb = src # hold original color
    # self.pin = id # palette index
    self.update = update
    self.values = {}
    # red
    self.values['r'] = tk.IntVar()
    # green
    self.values['g'] = tk.IntVar()
    # blue
    self.values['b'] = tk.IntVar()
    # color index in palette
    self.values['index'] = tk.IntVar()
    # description of what the color is for
    self.values['notes'] = tk.StringVar()
    # rgb converted back to 24 bit color
    self.values['ctext'] = tk.StringVar()
    
    # palette color id
    self.values['cid'] = tk.IntVar(value = id)
    
    # source color
    src = tuple(PD.FROMGBA(c) for c in src)
    c = '#%02x%02x%02x' % src
    self.ocbox = tk.Canvas(self, bg = c,
      width = 16, height = 16)
    # current color
    self.ncbox = tk.Canvas(self,
      width = 16, height = 16)
    
    self.ocbox.grid(column = 1, row = 0)
    self.ncbox.grid(column = 2, row = 0)
    self.reset_color(False)
    
    # description box for colors
    self.notes = tkx.EntryEx(self, 
      textvariable = self.values['notes']
      )
    self.notes.grid(
      column = 3,
      row = 0,
      columnspan = 2
      )
    
    reset = tk.Button(self,
      command = self.reset_color,
      text = 'reset')
    reset.grid(column = 5, row = 0)
    
    #color value widgets
    self.rbox = tkx.Spinbox2(self,
      bd = 3,
      from_ = 0, to = 31,
      width = 8,
      textvariable = self.values['r'],
      command = self.update_color,
      fg = "red")
    self.gbox = tkx.Spinbox2(self,
      bd = 3,
      width = 8,
      from_ = 0, to = 31,
      textvariable = self.values['g'],
      command = self.update_color,
      fg = "green")
    self.bbox = tkx.Spinbox2(self,
      bd = 3,
      width = 8,
      from_ = 0, to = 31,
      textvariable = self.values['b'],
      command = self.update_color,
      fg = "blue")
    self.rbox.grid(column = 1 , row = 1)
    self.gbox.grid(column = 2 , row = 1)
    self.bbox.grid(column = 3 , row = 1)
    
    # event binding for updating
    # after typing new value
    self.rbox.bind('<FocusOut>',
      lambda event:self.update_color())
    self.rbox.bind('<Return>',
      lambda event:self.update_color())
    self.gbox.bind('<FocusOut>',
      lambda event:self.update_color())
    self.gbox.bind('<Return>',
      lambda event:self.update_color())
    self.bbox.bind('<FocusOut>',
      lambda event:self.update_color())
    self.bbox.bind('<Return>',
      lambda event:self.update_color())
    
    self.rgbtext = tkx.EntryEx(self,
      width = 12,
      state = 'readonly',
      textvariable = self.values['ctext']
      )
    self.rgbtext.grid(column = 4, row = 1)
    
    self.obox = tkx.Spinbox2(self,
      bd = 3,
      width = 4,
      from_ = 0, to = 256,
      textvariable = self.values['cid']
      )
    self.obox.grid(column = 5, row = 1)
    
  def update_color(self, redraw = True):
    '''update canvas color'''
    r = PD.FROMGBA(self.values['r'].get())
    g = PD.FROMGBA(self.values['g'].get())
    b = PD.FROMGBA(self.values['b'].get())
    c = '#%02x%02x%02x' % (r,g,b)
    self.ncbox.configure(bg = c)
    c = ','.join(str(x) for x in (r,g,b))
    self.values['ctext'].set(c)
    if redraw and self.update: self.update(self)
  
  def reset_color(self, redraw = True):
    '''set color back to source color'''
    self.values['r'].set(self.ocrgb[PD.R])
    self.values['g'].set(self.ocrgb[PD.G])
    self.values['b'].set(self.ocrgb[PD.B])
    self.update_color(redraw)
    
    # if redraw:
      # self.update_color()
    # else:
      # c = ','.join(
        # str(PD.FROMGBA(x)) for x in self.ocrgb)
      # self.values['ctext'].set(c)
    
  def get_color(self, tc = False):
    '''return color as rgb tuple'''
    if tc:
      z = self.values['ctext'].get().split(',')
      c = tuple(int(x) for x in z)
      return c
      
    r = self.values['r'].get()
    g = self.values['g'].get()
    b = self.values['b'].get()
    return (r,g,b)
  
  def set_color(self, c, redraw = True):
    '''set color to given value
    :param c: rgb tuple
    :param redraw: if true, call update canvas
    '''
    self.values['r'].set(c[PD.R])
    self.values['g'].set(c[PD.G])
    self.values['b'].set(c[PD.B])
    self.update_color(redraw)
    
class Picture():
  '''class for handling the current image and palette group'''
  
  imgpath = ''
  srcimg = None
  srcpal = None
  altimg = None
  pin = 0 # current palette index
  palg = {}
  # altpal = None
  order = []

  def __init__(self):
    pass
  
  def change_image(self,newimgpath):
    sourceimg = Image.open(newimgpath)
    # convert image to palette mode
    self.index_image(sourceimg)
    self.altimg = self.srcimg.copy()
    self.imgpath = newimgpath
    
    # get current palette
    
    
    
  def index_image(self,srcpic):
    '''convert source image to palette mode'''
    # TODO: build new image using given palette
    
    # loop through pixels to remove unused colors later
    if srcpic.mode not in ('RGB','RGBA','P'):
      prompt = messagebox.showwarning(
        title = 'Input Image Error',
        message = 'Invalid Image Format'
        )
      raise ValueError('invalid image mode')
    
    # if srcpic.mode == 'P':
      # self.srcimg = srcpic
      # self.srcpal = PD.Palette(
        # flat = srcpic.getpalette())
      # return
    
    h = srcpic.height
    w = srcpic.width
    nid = [0] * (h*w)
    d = srcpic.getdata()
    pal = PD.Palette()
    if srcpic.mode == 'P':
      z = []
      for p in range(0,w*h):
        c = d[p]
        # add color if not already in list
        if c not in z:
          z.append(c)
        nid[p] = z.index(c)
      
      # build palette from used colors
      p = srcpic.getpalette()
      for i in z:
        x = i * 3
        c = p[x:x+3]
        pal.new_color(c)
    else: 
      for p in range(0,w*h):
        c = d[p][:3] # get rgb color
        i = pal.find_color(c)
        # add color if not already in Palette
        if i < 0:
          i = pal.new_color(c)
        nid[p] = i
    ni = Image.new(mode = 'P',size = (w,h))
    ni.putdata(nid)
    ni.putpalette(pal.flatten())
    
    # replace original image with indexed version
    self.srcimg = ni
    self.srcpal = pal
  
  def magnify(self,zoom=1):
    
    # zoom image to given level
    show = self.altimg.copy()
    if zoom > 0:
      w = show.width * zoom
      h = show.height * zoom
      show = show.resize((w,h))
    return show
  
  # FIX THIS
  def reorder(self, new):
    old = {}
    lenpal = len(self.srcpal)
    #map old color id to color rgb
    for c in range(lenpal):
      z = self.srcpal.get_color(c).flatten()
      old[c] = z
    
    order = {}
    newpal = PD.Palette(length = lenpal)
    # map old to new
    for c in range(lenpal):
      p = old[c]
      order[c] = new[p]
      #reorder source palette
      pz = self.srcpal.get_color(c)
      newpal.edit_color(new[p],pz)
    
    # if new and old order are the same,
    # copy source image instead of rebuilding
    if all(x == order[x] for x in order):
      nid = self.srcimg.getdata()
    else:
      #cycle through image to fix color order
      d = self.srcimg.getdata()
      w = self.srcimg.width
      h = self.srcimg.height
      nid = [0] * (w*h)
      for p in range(w*h):
        nid[p] = order[d[p]]
    
    self.altimg.putdata(nid)
  
  def change_pal(self, palid, dispal):
    '''store changes to current palette
      and load next palette'''
    pass

class App:
  def __init__(self,title = "Python GUI"):
    self.palf = None
    self.pic = Picture()
    self.root = tk.Tk()
    self.root.title(title)
    self.root.geometry('900x900')
    self.root.minsize(900,400)
    self._build_ui()
    self.root.mainloop()
  
  def _build_ui(self):
    ''' build the gui'''
    
    # hold any frame could be referenced later
    self.frames = {}
   
   # hold any widgets could be referenced later
    self.widgets = {}
    
    # hold all tk variables
    self.values = {} #dict for tk variables
    
    # the image to be formatted for the display
    self.sourceimg = None
   
   # the source image's orignal palette
    # self.sourcepal = None
    
    # formatted image for the display
    self.altimg = None
    # altimg as PhotoImage
    self.disimg = None
    
    # disimg as canvas object
    self.showimg = None
    
    # palette for formatted image
    self.dispal = None
    
    # list of color frames
    self.cfl = []
    
    mainframe = tk.Frame(self.root)
    self.frames["mainframe"] = mainframe
    mainframe.pack(fill = tk.BOTH, expand = True)
    
    mainframe.columnconfigure(0, weight = 1)
    mainframe.columnconfigure(1, weight = 1)
    
    mainframe.rowconfigure(0, weight = 9)
    # mainframe.rowconfigure(2, weight = 1)
    
    #image display area
    imgbox = tk.Frame(mainframe)
    imgbox.grid(row = 0, column = 0,
      pady = 5, padx = (5,0),
      sticky = (tk.N,tk.S,tk.W,tk.E))
    self.frames['imgbox'] = imgbox
    
    # imgbox.rowconfigure(0,weight=3)
    imgbox.rowconfigure(2, weight = 7)
    
    imgbox.columnconfigure(1, weight = 1)
    
    optionsbox = tk.Frame(imgbox)
    optionsbox.grid(row = 0,column = 1, 
      columnspan = 3,
      pady = 5,
      sticky = tk.N)
    self.frames['options'] = optionsbox
    
    #buttons
    groupnametext = tk.Label(optionsbox,text = "Name")
    groupnametext.grid(row = 3, 
      column = 0,
      sticky = tk.W)
    self.values['grouplabel'] = tk.StringVar()
    groupname = tk.Entry(optionsbox,
      textvariable = self.values['grouplabel'])
    groupname.grid(row = 3,
      column = 1,
      sticky = (tk.W,tk.E)
      )
    groupbutton1 = tk.Button(optionsbox,text = "Add")
    groupbutton2 = tk.Button(optionsbox,text = "Remove")
    groupbutton1.grid(row = 3,column = 2)
    groupbutton2.grid(row = 3,column = 3)
    
    self.values['zoom'] = tk.IntVar()
    zoomlabel = tk.Label(optionsbox,text = 'Zoom')
    zoomlabel.grid(row = 5,column = 0,sticky = tk.W)
    zoombox = tkx.Spinbox2(optionsbox,
      textvariable = self.values['zoom'],
      command = self.update_image,
      width = 8,
      from_ = 1, to = 16)
    zoombox.grid(row = 5,column = 1,sticky = tk.W)
    self.values['lzss'] = tk.IntVar()
    compcheck = tk.Checkbutton(optionsbox,
      text = 'LZSS',
      variable = self.values['lzss'])
    compcheck.grid(row = 5,column = 2)
    tkx.CreateToolTip(compcheck,
      'use lzss compression on this group of palettes')
    
    imgholder = tk.Canvas(imgbox)
    self.widgets['displayimg'] = imgholder
    imgscrolly = tk.Scrollbar(imgbox, 
      orient = tk.VERTICAL, 
      command = imgholder.yview)
    imgscrollx = tk.Scrollbar(imgbox, 
      orient = tk.HORIZONTAL,
      command = imgholder.xview)
    imgholder.grid(row = 2,column = 0,
      columnspan = 3, padx = (5,0),
      sticky = (tk.N,tk.S,tk.W,tk.E))
    imgscrollx.grid(row = 3,column = 0,
      columnspan = 3, padx = (5,0),
      sticky = (tk.W,tk.E))
    imgscrolly.grid(row = 2,
      column = 3,
      sticky = (tk.N,tk.S)
      )
    imgholder['xscrollcommand'] = imgscrollx.set
    imgholder['yscrollcommand'] = imgscrolly.set
    self.values['imgname'] = tk.StringVar(value = 'image name')
    
    imgbutt = tk.Button(imgbox,
      text = 'Change image',
      command = self.change_image)
    imgtext = tk.Label(imgbox,
      textvariable = self.values['imgname'])
    imgtext.grid(row = 1,column = 1)
    imgbutt.grid(row = 1,column = 2)
    
    #palette area
    palbox = tk.Frame(mainframe)
    # palbox['borderwidth'] = 5
    # palbox['relief'] = tk.GROOVE
    palbox.grid(row = 0,column = 1,
      padx = 5,pady = 5,
      sticky = (tk.N,tk.W,tk.S,tk.E))
    palbox.rowconfigure(1, weight = 1)
    
    self.frames['palbox'] = palbox
    self.frames['palette'] = tkx.ScrollFrame(palbox,
      padx = 10)
    buttres = tk.Button(palbox, 
      command = self.reset_colors,
      text = "Reset All")
    buttres.grid(row = 0,column = 1,sticky = tk.N)
    buttimp = tk.Button(palbox,
      text = "Import",
      command = self.paste_hex)
    buttimp.grid(row = 0,column = 2,sticky = tk.N)
    buttexp = tk.Button(palbox,
      text = "Export",
      command = self.clip_hex)
    buttexp.grid(row = 0,column = 3,sticky = tk.N)
    palentry = tk.Entry(palbox)
    palentry.grid(row = 0,column = 0,pady = 5)
    self.frames['palette'].grid(row = 1,rowspan = 3,
      column = 0, columnspan = 5,
      sticky = (tk.N,tk.W,tk.S,tk.E))
    tkx.CreateToolTip(buttimp,
      'import palette from clipboard')
    tkx.CreateToolTip(buttexp,
      'export palette to clipboard as hexadecimal')
    # self.frames['palette']['borderwidth']=3
    # self.frames['palette']['relief']=tk.RIDGE
    
  def _build_menu(self):
    self.menubar = tk.Menu(self.root)
    self.root.config(menu = self.menubar)
    file_menu = tk.Menu(self.menubar)
    file_menu.add_command(
      label = 'Exit',
      command = self.root.destroy)
    self.menubar.add_cascade(
      label = 'File',
      menu = file_menu,
      underline = 0)
    
  def change_image(self):
    '''change the displayed image'''
    
    newimgpath = askForFileIn((('png','*.png'),))
    if isValidFile(newimgpath):
      self.pic.change_image(newimgpath)
      self.dispal = PD.Palette()
      
      #reset zoom level
      self.values['zoom'].set(1)
      
      # write stuff for loading in existing palgroup
      
      #remove any previous color boxes
      for cf in self.cfl:
        cf.destroy()
      # self.cfl = []
      psize = len(self.pic.srcpal)
      cfs = [None] * psize
      for (x,c) in enumerate(self.pic.srcpal):
        c.r = PD.TOGBA(c.r)
        c.g = PD.TOGBA(c.g)
        c.b = PD.TOGBA(c.b)
        f = Colorbox(
          self.frames['palette'].casing,
          c.flatten(),x,self.update_image)
        f.config(
          width = self.frames['palbox']['width'],
          borderwidth = 2, relief = tk.RIDGE
          )
        f.grid(row = x, column = 0,
          padx = (5,0))
        
        # attach update function
        f.obox.configure(
          to = psize-1,
          command = lambda x = f: self.move_color(x))
        
        f.obox.bind("<FocusOut>",
          lambda event,x = f: self.move_color(x))
        f.obox.bind("<Return>",
          lambda event,x = f: self.move_color(x))
        
        cfs[x] = f
        #placeholder code until i fix dispal
        self.dispal.new_color(f.get_color(True))
        
      self.cfl = cfs
      # update color widgets in 'palette' frame
      # update source palette
      display = self.widgets['displayimg']
      self.showimg = display.create_image(
        (5,5),
        image = self.disimg
        )
      display.config(
        scrollregion = display.bbox(tk.ALL))
      self.update_image()
      self.values['imgname'].set(newimgpath.stem)
    
  def index_image(self):
    '''convert sourceimg to palette mode'''
    #TODO: build new image using given palette
    
    if self.sourceimg.mode == 'P':
      return
    if self.sourceimg.mode not in ('RGB','RGBA'):
      raise ValueError('invalid image mode')
    h = self.sourceimg.height
    w = self.sourceimg.width
    nid = [0] * (h*w)
    d = self.sourceimg.getdata()
    pal = PD.Palette()
    for p in range(0,w*h):
      c = d[p][:3] #get rgb color
      i = pal.find_color(c)
      #add color if not already in Palette
      if i < 0:
        i = pal.new_color(c)
      nid[p] = i
    ni = Image.new(mode = 'P',size = (w,h))
    ni.putdata(nid)
    ni.putpalette(pal.flatten())
    #replace original image with indexed version
    self.sourceimg = ni
  
  def grab_pal(self):
    n = len(self.cfl)
    #form palette from widget values
    newpal = PD.Palette(length = n)
    for x in range(n):
      cf = self.cfl[x]
      c = cf.get_color()
      newpal.edit_color(cf.values['cid'].get(),c)
    newpal.to_gba_hex()
    return newpal
    
  def update_image(self,cf = None):
    '''update imagine on canvas'''
    # do nothing if no image
    if not self.pic.srcimg: return
    
    if cf:
      c = cf.get_color(True)
      self.dispal.edit_color(cf.values['cid'].get(),c)
    
    z = self.values['zoom'].get()
    newimg = self.pic.magnify(z)
    newimg.putpalette(self.dispal.flatten())
    
    self.disimg = ImageTk.PhotoImage(
      image=newimg)
    
    display = self.widgets['displayimg']
    display.itemconfig(
      self.showimg,image = self.disimg)
    display.configure(
      scrollregion = display.bbox(tk.ALL))
  
  def update_palette(self):
    for cf in self.cfl:
      c = cf.get_color(True)
      self.dispal.edit_color(cf.values['cid'].get(),c)
  
  def reset_colors(self):
    '''reset every color frame then update the display'''
    
    for cf in self.cfl:
      cf.reset_color(False)
    self.update_palette()
    self.update_image()
  
  def move_color(self,cf):
    #do nothing if no color frames
    if not self.cfl: return
    
    #fix if input is out of range
    c = cf.values['cid']
    if c.get() < 0: c.set(0)
    elif c.get() >= len(self.cfl):
      c.set(len(self.cfl)-1)
    
    clist = self.cfl.copy()
    #sort color frames by color index
    clist.sort(key = lambda x: x.values['cid'].get())
    x = clist.index(cf)
    #remove item from list
    clist.pop(x)
    #move item to place in list
    clist.insert(cf.values['cid'].get(),cf)
    #reorder color index for color frames
    for x,c in enumerate(clist): c.values['cid'].set(x)
    
    #build second dict from color frames
    new = {}
    #map color rgb to color id
    for cf in self.cfl:
      new[cf.ocrgb] = cf.values['cid'].get()
    
    self.pic.reorder(new)

    self.update_palette()
    self.update_image()
  
  def clip_hex(self):
    '''copy palette to clipboard'''
    
    # do nothing if no color frames exist
    if not self.cfl: return
    
    self.root.clipboard_clear()
    pal = self.grab_pal()
    palclip = pal.to_gba_hex()
    self.root.clipboard_append(palclip)
    self.root.update()
    prompt = messagebox.showinfo(
      title = 'Copied to Clipboard',
      message = palclip)
  
  def paste_hex(self):
    '''copy from palette clipboard'''
    
    # do nothing if no color frames exist
    if not self.cfl: return
    
    try:
      paste = self.root.clipboard_get()
    except tk.TclError:
      paste = ''
    
    if paste and ishex(paste): 
      if self.cfl:
        pal = PD.Palette.from_gba_hex(paste)
        #use pasted hex to build display palette
        for cf in self.cfl:
          c = pal.get_color(cf.values['cid'].get())
          cf.set_color(c.flatten(),True)
        #update display palette:
        for p in pal.colors:
          p.r = PD.FROMGBA(p.r)
          p.g = PD.FROMGBA(p.g)
          p.b = PD.FROMGBA(p.b)
        self.dispal = pal
        self.update_image()
    else:
      prompt = messagebox.showwarning(
        title = 'Import Error',
        message = 'Invalid input for Import')



if __name__ == '__main__':
  app = App("Recolor")
  
  
  """
  every time any rbg value changes,
  update image palette and image
  
  
  build tk window
  Frame
    Frame
      hold image for recoloring
    Frame
      hold list of colors
    Frame
      hold options
  features
    import palette from clipboard
    export palette from clipboard
    import palette group
    export palette group
    save/load all palettes as xml file
      convert xml to EA installer
    
  
  palette group is:
    all the palettes of a unit in each team
    autofill data
    
  reorder index
    
  """

'''
    to do list:
    [ ]cycle through palette groups
    [ ]cycle through palettes in current palette group
    [ ]export all palette groups as EA file
    [ ]add new palette
    [ ]delete current palette
    [ ]add new palette group
    [ ]delete current palette group
    [ ]export current palette group as bin file
    [+]select image for current palette group
    [+]write label for palette group
    [+]write note for palette
    [ ]write note for color
    [+]reset color
    [+]reset all colors in palette
    [ ]way to add in the stuff like set{} and ids
    [ ]consider way to add in comments
    [+]zoom for display image
    [ ]save to toml
    [ ]load from toml
    [+]reorder colors in palette
'''

