#!/bin/env python3

# import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
import xml.etree.ElementTree as ET

from PIL import Image,ImageTk
import palette as PD

#File loading/saving functions
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

class palstruct():
  gindex = 0
  pindex = 0
  data = {}
  
  def __init__(self):
    self.data['palg'] = []
  
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
    return self.data['palg'][gindex]

class ColorBox(tk.Frame):
  '''set of widgets made for the rgb section'''
  def __init__(self,parent,src,id,update=None,*args,**kwargs):
    '''
    :param parent: parent widget
    :param src: source color (tuple)
    :param id: int color number in palette
    '''
    super().__init__(parent, *args, **kwargs)
    self.ocrgb = src #hold original color
    self.pin = id #palette index
    self.update = update
    self.values = {}
    self.values['r']=tk.IntVar()
    self.values['g']=tk.IntVar()
    self.values['b']=tk.IntVar()
    self.values['index'] = tk.IntVar()
    self.values['notes'] = tk.StringVar()
    self.values['ctext'] = tk.StringVar()
    
    # source color
    src = tuple(PD.FROMGBA(c) for c in src)
    c = '#%02x%02x%02x' % src
    self.ocbox = tk.Canvas(self, bg = c,
      width = 16, height = 16)
    # current color
    self.ncbox = tk.Canvas(self,
      width = 16, height = 16)
    
    self.ocbox.grid(column=1,row=1)
    self.ncbox.grid(column=2,row=1)
    self.reset_color()
    
    #color value widgets
    rbox = Spinbox(self,
      bd = 3,
      from_=0, to=31,
      width=8,
      textvariable=self.values['r'],
      command=self.update_color,
      fg = "red")
    gbox = Spinbox(self,
      bd = 3,
      width=8,
      from_=0, to=31,
      textvariable=self.values['g'],
      command=self.update_color,
      fg = "green")
    bbox = Spinbox(self,
      bd = 3,
      width=8,
      from_=0, to=31,
      textvariable=self.values['b'],
      command=self.update_color,
      fg = "blue")
    rbox.grid(column=1,row=0)
    gbox.grid(column=2,row=0)
    bbox.grid(column=3,row=0)
    #text box for colors
    notes = tk.Entry(self, 
      textvariable = self.values['notes']
      )
    reset = tk.Button(self,
      command=self.reset_color,
      text='reset')
    reset.grid(column=4,row=0)
    
  def update_color(self):
    r = PD.FROMGBA(self.values['r'].get())
    g = PD.FROMGBA(self.values['g'].get())
    b = PD.FROMGBA(self.values['b'].get())
    c = '#%02x%02x%02x' % (r,g,b)
    self.ncbox.configure(bg = c)
    if self.update: self.update(self)
  
  def reset_color(self,redraw=True):
    self.values['r'].set(self.ocrgb[PD.R])
    self.values['g'].set(self.ocrgb[PD.G])
    self.values['b'].set(self.ocrgb[PD.B])
    if redraw: self.update_color()
    
  def get_color(self):
    r = self.values['r'].get()
    g = self.values['g'].get()
    b = self.values['b'].get()
    return (r,g,b)
  
class Spinbox(tk.Spinbox):
  '''Spinbox, but with scrolling to change values'''
  def __init__(self,parent,*args,**kwargs):
    super().__init__(parent, *args, **kwargs)
    self.bind('<MouseWheel>', self._mousewheel)
    self.bind('<Button-4>', self._mousewheel)
    self.bind('<Button-5>', self._mousewheel)
    
  def _mousewheel(self,event):
    if event.num == 5 or event.delta == -120:
      self.invoke('buttondown')
    elif event.num == 4 or event.delta == 120:
      self.invoke('buttonup')
    
class ScrollFrame(tk.Frame):
  '''made to contain other widgets'''
  def __init__(self,parent,*args,**kwargs):
    super().__init__(parent, *args, **kwargs)
    
    self.canvas = tk.Canvas(self)
    self.casing = tk.Frame(self.canvas)
    
    self.sbary = tk.Scrollbar(self, width=20,
      orient=tk.VERTICAL,
      command = self.canvas.yview)
    self.canvas['yscrollcommand']=self.sbary.set
    self.canvas.grid(column=0,
      row=0,sticky=(tk.N,tk.W,tk.S,tk.E))
    self.sbary.grid(column=1,
      row=0,sticky=(tk.N,tk.S))
    
    self.canvas_window = \
      self.canvas.create_window((4,4),
      anchor='nw',
      window = self.casing,
      tags="self.casing")
    self.casing.bind(
      "<Configure>",self._configurecasing)
    self.canvas.bind(
      "<Configure>",self._configurecanvas)
    
    self.casing.bind("<Enter>",self._enter)
    self.casing.bind("<Leave>",self._leave)
    
  def _configurecasing(self,event):
    '''Adjust scroll region to match casing'''
    self.canvas.configure(
      scrollregion=self.canvas.bbox("all"))
  def _configurecanvas(self,event):
    '''Adjust canvas window to match casing'''
    self.canvas.itemconfig(self.canvas_window,
      width = event.width)
  def _mousewheel(self,event):
    '''scroll wheel event'''
    self.canvas.yview_scroll(
      int(-1*(event.delta/120)),"units")
    
  def _enter(self,event):
    '''bind wheel events when the cursor enters'''
    self.canvas.bind(
      "<MouseWheel>",self._mousewheel)
  def _leave(self,event):
    '''unbind wheel events when the cursorl leaves'''
    self.canvas.unbind("<MouseWheel>")

class ToolTip(object):
	'''create a tooltip for a given widget'''
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0

	def showtip(self, text):
		"Display text in tooltip window"
		self.text = text
		if self.tipwindow or not self.text:
			return
		x, y, cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx() + 57
		y = y + cy + self.widget.winfo_rooty() +27
		self.tipwindow = tw = tk.Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(tw, text=self.text, justify=tk.LEFT,
					  background="#ffffe0", relief=tk.SOLID, borderwidth=1,
					  font=("tahoma", "8", "normal"))
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

def CreateToolTip(widget, text):
	toolTip = ToolTip(widget)
	def enter(event):
		toolTip.showtip(text)
	def leave(event):
		toolTip.hidetip()
	widget.bind('<Enter>', enter)
	widget.bind('<Leave>', leave)

class App:
  def __init__(self,title="Python GUI"):
    self.root = tk.Tk()
    self.root.title(title)
    self.root.geometry('900x600')
    self._build_ui()
    self.root.mainloop()
    self.colors = []
  
  def _build_ui(self):
    self.frames = {}
    self.widgets = {}
    self.values = {} #dict for tk variables
    self.sourceimg = None
    self.sourcepal = None
    self.showimg = None
    self.disimg = None
    self.dispal = None
    self.cfl = []
    mainframe = tk.Frame(self.root)
    self.frames["mainframe"] = mainframe
    mainframe.pack()
    
    '''
    buttons to make:
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
    [ ]reset all colors in palette
    [ ]way to add in the stuff like set{} and ids
    [ ]consider way to add in comments
    [ ]zoom for display image
    '''
    
    #image display area
    imgbox = tk.Frame(mainframe)
    imgbox.grid(row=0,column=0,columnspan = 4,
      rowspan = 3,)
    self.frames['imgbox'] = imgbox
    imgholder = tk.Canvas(imgbox)
    self.widgets['displayimg'] = imgholder
    imgscrolly = tk.Scrollbar(imgbox, 
      orient=tk.VERTICAL, 
      command=imgholder.yview)
    imgscrollx = tk.Scrollbar(imgbox, 
      orient=tk.HORIZONTAL,
      command=imgholder.xview)
    imgholder.grid(row=1,column=0,columnspan=3,
      sticky=tk.W)
    imgscrollx.grid(row=2,column=0,columnspan=3,
      sticky=(tk.W,tk.E))
    imgscrolly.grid(row=1,column=3,sticky=(tk.N,tk.S))
    imgholder['xscrollcommand'] = imgscrollx.set
    imgholder['yscrollcommand'] = imgscrolly.set
    self.values['imgname']= tk.StringVar(value='image name')
    imgbutt = tk.Button(imgbox,
      text='Change image',
      command=self.change_image)
    imgtext = tk.Label(imgbox,
      textvariable=self.values['imgname'])
    imgtext.grid(row=0,column=1)
    imgbutt.grid(row=0,column=2)
    
    #palette area
    palbox = tk.Frame(mainframe)
    # palbox['borderwidth'] = 5
    # palbox['relief'] = tk.GROOVE
    palbox.grid(row=0,column=4,columnspan=6,
      rowspan=8,padx=2,
      sticky=(tk.N,tk.W,tk.S,tk.E))
    self.frames['palbox'] = palbox
    self.frames['palette'] = ScrollFrame(palbox,padx=10)
    buttres = tk.Button(palbox, 
      command = self.reset_colors,
      text = "Reset All")
    buttres.grid(row=0,column=1,sticky=tk.N)
    buttimp = tk.Button(palbox,text="Import")
    buttimp.grid(row=0,column=2,sticky=tk.N)
    buttexp = tk.Button(palbox,
      text="Export",
      command = self.clip_hex)
    buttexp.grid(row=0,column=3,sticky=tk.N)
    palentry = tk.Entry(palbox)
    palentry.grid(row=0,column=0)
    self.frames['palette'].grid(row=1,rowspan=3,
      column=0, columnspan=5,
      sticky=(tk.W,tk.E))
    CreateToolTip(buttimp,
      'import palette from clipboard')
    CreateToolTip(buttexp,
      'export palette to clipboard as hexadecimal')
    # self.frames['palette']['borderwidth']=3
    # self.frames['palette']['relief']=tk.RIDGE
    
    #buttons
    groupnametext = tk.Label(mainframe,text="Name")
    groupnametext.grid(row=3,column=0,sticky=tk.W)
    self.values['grouplabel'] = tk.StringVar()
    groupname = tk.Entry(mainframe,
      textvariable=self.values['grouplabel'])
    groupname.grid(row=3,column=1,sticky=(tk.W,tk.E))
    groupbutton1 = tk.Button(mainframe,text="Add")
    groupbutton2 = tk.Button(mainframe,text="Remove")
    groupbutton1.grid(row=3,column=2)
    groupbutton2.grid(row=3,column=3)
    
    self.values['zoom'] = tk.IntVar()
    zoomlabel = tk.Label(mainframe,text='Zoom')
    zoomlabel.grid(row=5,column=0,sticky=tk.W)
    zoombox = Spinbox(mainframe,
      textvariable=self.values['zoom'],
      command = self.update_image,
      width = 8,
      from_ = 1, to= 16)
    zoombox.grid(row=5,column=1,sticky=tk.W)
    self.values['lzss'] = tk.IntVar()
    compcheck = tk.Checkbutton(mainframe,
      text = 'LZSS',
      variable= self.values['lzss'])
    compcheck.grid(row=5,column=2)
    CreateToolTip(compcheck,
      'use lzss compression on this group of palettes')
    
  def _build_menu(self):
    self.menubar = tk.Menu(self.root)
    self.root.config(menu=self.menubar)
    file_menu = tk.Menu(self.menubar)
    file_menu.add_command(label='Exit',command=self.root.destroy)
    self.menubar.add_cascade(label='File',menu=file_menu, underline = 0)
    
  def change_image(self):
    '''change the displayed image'''
    newimgpath = askForFileIn((('png','*.png'),))
    if isValidFile(newimgpath):
      self.sourceimg = Image.open(newimgpath)
      #convert image to palette mode
      self.index_image()
      #get original palette
      self.showimg = ImageTk.PhotoImage(
        # file=newimgpath)
        image=self.sourceimg)
      # do palette stuff here
      self.sourcepal = PD.Palette(
        flat=self.sourceimg.getpalette())
      self.dispal = PD.Palette(
        flat=self.sourceimg.getpalette())
      #reset zoom level
      self.values['zoom'].set(1)
      #remove any previous color boxes
      for cf in self.cfl:
        cf.destroy()
      cfs = [None] * len(self.sourcepal.colors)
      for (x,c) in enumerate(self.sourcepal.colors):
        c.r = PD.TOGBA(c.r)
        c.g = PD.TOGBA(c.g)
        c.b = PD.TOGBA(c.b)
        f = ColorBox(
          self.frames['palette'].casing,
          c.flatten(),x,self.update_image)
        f.config(
          width=self.frames['palbox']['width']
          )
        f.grid(row=x,column=0)
        cfs[x] = f
      self.cfl = cfs
      # update color widgets in 'palette' frame
      # update source palette
      display = self.widgets['displayimg']
      self.disimg = display.create_image(
        (5,5),
        image=self.showimg
        )
      display.config(
        scrollregion=display.bbox(tk.ALL))
      self.values['imgname'].set(newimgpath.name)
    
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
      nid[p]= i
    ni = Image.new(mode='P',size=(w,h))
    ni.putdata(nid)
    ni.putpalette(pal.flatten())
    #replace original image with indexed version
    self.sourceimg = ni
  
  def grab_pal(self):
    n = len(self.cfl)
    #form palette from widget values
    newpal = PD.Palette(length=n)
    for x in range(n):
      cf = self.cfl[x]
      c = cf.get_color()
      newpal.edit_color(cf.pin,c)
    newpal.to_gba_hex()
    return newpal
    
  def update_image(self,cf = None):
    # do nothing if no image
    if not self.sourceimg: return
    
    if cf:
      c = cf.get_color()
      c = tuple(PD.FROMGBA(n) for n in c)
      self.dispal.edit_color(cf.pin,c)
    newpal = self.dispal.flatten()
    # else:
      # newpal = self.grab_pal().flatten()
      # newpal = tuple(FROMGBA(n) for n in newpal)
    newimg = self.zoomed_image()
    newimg.putpalette(newpal)
    self.showimg = ImageTk.PhotoImage(
      image=newimg)
    display = self.widgets['displayimg']
    display.itemconfig(
      self.disimg,image=self.showimg)
    display.configure(
      scrollregion=display.bbox(tk.ALL))
  
  def update_palette(self):
    for cf in self.cfl:
      c = cf.get_color()
      c = tuple(PD.FROMGBA(n) for n in c)
      self.dispal.edit_color(cf.pin,c)
  
  def reset_colors(self):
    for cf in self.cfl:
      cf.reset_color(False)
    self.update_palette()
    self.update_image()
  
  def zoomed_image(self):
    z = self.values['zoom'].get()
    newimg = self.sourceimg.copy()
    newimg.putpalette(self.dispal.flatten())
    if z > 0:
      w = newimg.width * z
      h = newimg.height * z
      newimg = newimg.resize((w,h))
    return newimg
  
  def clip_hex(self):
    if not self.cfl: return
    
    self.root.clipboard_clear()
    pal = self.grab_pal()
    palclip = pal.to_gba_hex()
    self.root.clipboard_append(palclip)
    self.root.update()
    prompt = messagebox.showinfo(
      title = 'Copied to Clipboard',
      message = palclip)
  



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