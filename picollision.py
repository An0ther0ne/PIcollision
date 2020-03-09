#-*- coding: utf-8 -*-

import PySimpleGUI 	as sg
import numpy as np
import cv2

# --- Global Constants

_DEBUG    = True
MASSRATIO = 1000000
WIDTH     = 400
HEIGHT    = WIDTH
MAX_X	  = 10

# --- Classes Definition

class BaseObj:
	def __init__(self):
		self._objects = []
	def Append(self, obj):
		self._objects.append(obj)
		return len(self._objects)
	def __getitem__(self, index):
		if index <= len(self._objects):
			return self._objects[index]
		else:
			return None
	def __iter__(self):
		self._curcnt = 0
		return self
	def __next__(self):
		if self._curcnt < len(self._objects):
			self._curcnt += 1
			return self.__getitem__(self._curcnt - 1)
		else:
			raise StopIteration
	count   = property(lambda self : len(self._objects))

class Slider:
	_val = -1
	def __init__(self, name, desc, min=1, max=100, default=50, multiply=1):
		self._name = name
		self._desciption = desc
		self._key = '-s_' + name + '-'
		self._min = min
		self._max = max
		self._def = default
		self._mul = multiply
	def set_val(self, value):
		if self._val != value:
			self._val = value
			return True
		else:
			return False
	name = property(lambda self : self._name)
	desc = property(lambda self : self._desciption)
	key  = property(lambda self : self._key)
	val  = property(lambda self : self._val, set_val)
	meaning = property(lambda self : self._val * self._mul if self._mul > 0 else 10 ** self._val)
	min  = property(lambda self : self._min)
	max  = property(lambda self : self._max)
	default = property(lambda self : self._def)

class Sliders(BaseObj):
	def __init__(self):
		BaseObj.__init__(self)
		self._layout  = []
	def Append(self, slider, width):
		self._layout.append([
			sg.Text(
				slider.desc + ':',
				size=(6, 1)),
			sg.Slider(
				range=(slider.min, slider.max),
				disable_number_display=True,
				default_value=slider.default,
				orientation='h',
				size=(width, 20),
				key=slider.key
			)
		])
		return BaseObj.Append(self, slider)
	def get_slider_value(self, key):
		for slider in self._objects:
			if slider.name == key:
				return slider.meaning
		return 0
	def get_sliders(self):
		return self._objects
	def get_caption(self):
		caption = ''
		for slider in self._objects:
			value = slider.meaning
			if value > 10:
				caption += slider.desc + '={:<10.0f} '.format(value)
			elif value > 0.999:
				caption += slider.desc + '={:<10.1f} '.format(value)
			else:
				caption += slider.desc + '={:<10.3f} '.format(value)
		return caption
	layout = property(lambda self : self._layout)

class Frame:
	_window_element = None
	_minsize = 0
	def __init__(self, width, height, key):
		self._width   = width
		self._height  = height
		self._minsize = width
		if self._minsize > height:
			self._minsize = height
		self._key = key
		self._image = np.zeros((height, width, 3), dtype="uint8")
	def Draw(self):
		frame = self._image.copy()
		return frame
	def Update(self, img):
		self._window_element.update(data=cv2.imencode('.png', img)[1].tobytes())
	def set_window_element(self, window):
		self._window_element = window[self._key]
	wndelem = property(lambda self : self._window_element, set_window_element)
	key     = property(lambda self : self._key)
	width   = property(lambda self : self._width)
	height  = property(lambda self : self._height)
	image   = property(lambda self : self._image)
	minsize = property(lambda self : self._minsize)

class LeftFrame(Frame):
	def __init__(self, width, height):
		Frame.__init__(self, width, height, '-leftimage-')

class RghtFrame(Frame):
	def __init__(self, width, height):
		Frame.__init__(self, width, height, '-rghtimage-')

class Frames(BaseObj):
	_width    = 0
	_minwidth = 0
	def Append(self, frame):
		self._width += frame.width
		if self._minwidth > frame.width:
			self._minwidth = frame.width
		return BaseObj.Append(self, frame)
	def Update(self, blocks):
		for frame in self._objects:
			img = frame.image
			frame.Update(img)
	width   = property(lambda self : self._width)

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
	def Go(self, dt):
		self._xposition += self._velocity * dt
		if self._xposition < 0:
			self._xposition = 0
			self._velocity = -self._velocity
	def Draw(self, frame):
		pass
	def set_mass(self, val):
		self._mass = val
	def set_velo(self, val):
		self._velocity = val
	def set_xposition(self, val):
		self._xposition = val
	def set_size(self, val):
		self._size = val
	mass = property(lambda self : self._mass, set_mass)
	velo = property(lambda self : self._velocity, set_velo)
	posx = property(lambda self : self._xposition, set_xposition)
	size = property(lambda self : self._size, set_size)

class Scene(BaseObj):
	def __init__(self, frameset, sliders):
		BaseObj.__init__(self)
		self._frameset = frameset
		self._sliders = sliders
	def Reset(self):
		for block in self._objects:
			block.Reset()
	def Draw(self):
		for obj in self._objects:
			obj.Go(self._sliders.get_slider_value('Dt'))
			obj.Draw(self._frameset[0])
		self._frameset.Update(self._objects)

# --- Instances Implementation

frames = Frames()
frames.Append(LeftFrame(WIDTH * 3 // 2, HEIGHT))
frames.Append(RghtFrame(WIDTH, HEIGHT))

sliders = Sliders()
sliders.Append(Slider('Dt',   'Delta T', multiply=0.001, max=200),  frames.width // 12)
sliders.Append(Slider('Vel',  'Velocity'), frames.width // 12)
sliders.Append(Slider('Mass', 'Mass', min=0, max=10, default=0, multiply=0),     frames.width // 12)

scene = Scene(frames, sliders)
scene.Append(Block(1, 1, 0))
scene.Append(Block(MASSRATIO, MAX_X-1, -MAX_X))

# --- Main Window

MainLayout = []
MainLayout.append([sg.Image(filename='', key=frame.key) for frame in frames])
MainLayout.append([sg.Text('', size=(80,1), text_color='Green', font='bold', key='-values-')])
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
caption_elem = MainWindow['-values-']
Redraw  = 0

while True:
	event, values = MainWindow.Read(timeout=10)
	if event == 'Exit' or event == None:
		break
	scene.Draw()
	for slider in sliders:
		if slider.set_val(values[slider.key]):
			Redraw += 1
	if Redraw:
		Redraw = 0
		caption_elem.update(sliders.get_caption())
