#-*- coding: utf-8 -*-

import PySimpleGUI 	as sg
import numpy as np
import cv2

# --- Global Constants

_DEBUG    = True
MASSRATIO = 1000000
WIDTH     = 400
HEIGHT    = WIDTH

# --- Classes Definition

class Slider:
	_name = ''
	_desciption = ''
	_val = -1
	_key = ''
	def __init__(self, name, desc, min=1, max=100):
		self._name = name
		self._desciption = desc
		self._key = '-s_' + name + '-'
		self._min = min
		self._max = max
	def get_name(self):
		return self._name
	def get_desc(self):
		return self._desciption
	def get_key(self):
		return self._key
	def get_min(self):
		return self._min
	def get_max(self):
		return self._max
	def get_val(self):
		return self._val
	def set_val(self, value):
		if self._val != value:
			self._val = value
			return True
		else:
			return False
	name = property(get_name)
	desc = property(get_desc)
	key  = property(get_key)
	val  = property(get_val, set_val)
	min  = property(get_min)
	max  = property(get_max)

class Sliders:
	_sliders = []
	_layout  = []
	_count   = 0
	def Append(self, slider, width):
		self._sliders.append(slider)
		self._layout.append([
			sg.Text(slider.desc + ':', size=(6,1)),
			sg.Slider(
				range=(1,100),
				disable_number_display=True,
				default_value=50,
				orientation='h',
				size=(width,20),
				key=slider.key
			)
		])
		self._count += 1
		return self._count
	def get_count(self):
		return self._count
	def get_slider(self, num):
		if num <= len(self._sliders):
			return self._sliders[num]
		else:
			return None
	def get_sliders(self):
		return self._sliders
	def get_layout(self):
		return self._layout
	def __iter__(self):
		self._currnt = 0
		return self
	def __next__(self):
		if self._currnt < self._count:
			self._currnt += 1
			return self.get_slider(self._currnt - 1)
		else:
			raise StopIteration
	count  = property(get_count)
	all    = property(get_sliders)
	layout = property(get_layout)

class Frame:
	_window_element = None
	def __init__(self, width, height, key):
		self._width  = width
		self._height = height
		self._key = key
		self._image = np.zeros((height, width, 3), dtype="uint8")
	def Draw(self):
		frame = self._image.copy()
		return frame
	def Update(self):
		self._window_element.update(data=cv2.imencode('.png', self.Draw(self))[1].tobytes())
	def GetKey(self):
		return self._key
	def GetWidth(self):
		return self._width
	def GetHeight(self):
		return self._height
	def get_image(self):
		return self._image
	def get_window_element(self):
		return self._window_element
	def set_window_element(self, window):
		self._window_element = window[self._key]
	key     = property(GetKey)
	width   = property(GetWidth)
	height  = property(GetHeight)
	wndelem = property(get_window_element, set_window_element)
	image   = property(get_image)

class LeftFrame(Frame):
	def __init__(self, width, height):
		Frame.__init__(self, width, height, '-leftimage-')
	def Draw(self, params):
		return Frame.Draw(self)

class RghtFrame(Frame):
	def __init__(self, width, height):
		Frame.__init__(self, width, height, '-rghtimage-')
	def Draw(self, params):
		return Frame.Draw(self)

class Frames:
	_frames = []
	_width  = 0
	_count  = 0
	def Append(self, frame):
		self._frames.append(frame)
		self._width += frame.width
		self._count += 1
		return self._count
	def Update(self):
		for frame in self._frames:
			frame.Update()
	def get_count(self):
		return len(self._frames)
	def get_width(self):
		return self._width
	def __getitem__(self, index):
		if index <= len(self._frames):
			return self._frames[index]
		else:
			return None
	def __iter__(self):
		self._currnt = 0
		return self
	def __next__(self):
		if self._currnt < self._count:
			self._currnt += 1
			return self.__getitem__(self._currnt - 1)
		else:
			raise StopIteration
	width   = property(get_width)
	count   = property(get_count)

class Block:
	_size      = 0
	_mass      = 0
	_velocity  = 0
	_velinit   = 0
	_xposition = 0
	_xstart    = 0
	def __init__(self, mass, posx, velo):
		self._mass = mass
		self._xposition = posx
		self._xstart = posx
		self._velocity = velo
		self._velinit  = velo
	def Reset(self):
		self._velocity  = self._velinit
		self._xposition = self._xstart
	def get_mass(self):
		return self._mass
	def set_mass(self, val):
		self._mass = val
	def get_velo(self):
		return self._velocity
	def set_velo(self, val):
		self._velocity = val
	def get_xposition(self):
		return self._xposition
	def set_xposition(self, val):
		self._xposition = val
	def get_size(self):
		return self._size
	def set_size(self, val):
		self._size = val
	mass = property(get_mass, set_mass)
	velo = property(get_velo, set_velo)
	posx = property(get_xposition, set_xposition)
	size = property(get_size, set_size)

class Scene:
	_objects = []
	_frame  = None	
	_count   = 0
	_height = 0
	_width  = 0
	_minsize= 0
	def __init__(self, frame):
		self._height, self._width = frame.image.shape[:2]
		self._minsize = self._height
		if self._minsize > self._width:
			self._minsize = self._width
	def Append(self, obj, dx):
		self._objects.append(obj) 
		self._count += 1
	def Reset(self):
		for obj in _self._objects:
			obj.Reset()

class LScene(Scene):
	pass
	
class RScene(Scene):
	pass	

# --- Instances Implementation

frames = Frames()
frames.Append(LeftFrame(WIDTH * 3 // 2, HEIGHT))
frames.Append(RghtFrame(WIDTH, HEIGHT))

sliders = Sliders()
sliders.Append(Slider('Dt',   'Delta T'),  frames.width // 12)
sliders.Append(Slider('Vel',  'Velocity'), frames.width // 12)
sliders.Append(Slider('Mass', 'Mass'),     frames.width // 12)

# leftbrick  = Block(1, 0)
# rightbrick = Block(MASSRATIO, 10)

lscene = LScene(frames[0])
rscene = RScene(frames[1])

# --- Main Window

MainLayout = []
MainLayout.append([sg.Image(filename='', key=frame.key) for frame in frames])
MainLayout.append([sg.Text('', size=(40,1), text_color='Yellow', font='bold', key='-values-')])
MainLayout.append([
	sg.Frame(
		'Options:',
		sliders.layout,
		font='Any 11',
		title_color='blue',
		pad=(5,10),
		element_justification = 'left',
		title_location = sg.TITLE_LOCATION_TOP_LEFT,
)])

MainLayout.append([
		sg.Button('Start', size=(10,1), pad=(frames.width // 9,10), font='Hevletica 14'),
		sg.Button('Stop', size=(10,1), pad=(frames.width // 9,10), font='Hevletica 14'),
		sg.Button('Exit', size=(10,1), pad=(frames.width // 9,10), font='Hevletica 14'),
])

# --- Main Program

MainWindow = sg.Window('Pi number from collision calculation', MainLayout, no_titlebar=False, location=(0,0))
for frame in frames:
	frame.wndelem = MainWindow
Redraw  = 0

while True:
	event, values = MainWindow.Read(timeout=10)
	if event == 'Exit' or event == None:
		break
	for slider in sliders:
		if slider.set_val(values[slider.key]):
			Redraw += 1
	if Redraw:
		Redraw = 0
		if _DEBUG: print('+++ Redraw', flush=True)
		frames.Update()
