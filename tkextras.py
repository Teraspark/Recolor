import tkinter as tk
# from tkinter import ttk

'''
Extra tk widgets for qol
'''

class Spinbox2(tk.Spinbox):
  '''Spinbox, but with scrolling to change values'''
  def __init__(self,parent,*args,**kwargs):
    super().__init__(parent, *args, **kwargs)
    # bind event for scrolling
    self.bind('<MouseWheel>', self._mousewheel)
    self.bind('<Button-4>', self._mousewheel)
    self.bind('<Button-5>', self._mousewheel)
    
  def _mousewheel(self,event):
    '''handles scrolling to change value'''
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
    self.canvas.pack(side = tk.LEFT,
      fill = tk.BOTH,
      expand = True)
    self.sbary.pack(side = tk.LEFT,fill=tk.Y)
    
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
	'''create a tooltip:
  produces hover text when over given object'''
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0

	def showtip(self, text):
		'''Display text in tooltip window'''
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
		'''remove tooltip window text'''
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

class EntryEx(tk.Entry):
    """
    Extended entry widget that includes a context menu
    with Copy, Cut and Paste commands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = tk.Menu(self, tearoff=False)
        self.menu.add_command(label="Copy", command=self.popup_copy)
        self.menu.add_command(label="Cut", command=self.popup_cut)
        self.menu.add_separator()
        self.menu.add_command(label="Paste", command=self.popup_paste)
        self.bind("<Button-3>", self.display_popup)

    def display_popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def popup_copy(self):
        self.event_generate("<<Copy>>")

    def popup_cut(self):
        self.event_generate("<<Cut>>")

    def popup_paste(self):
        self.event_generate("<<Paste>>")
