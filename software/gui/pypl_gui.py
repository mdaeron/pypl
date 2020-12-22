#! /usr/bin/env python3

import pyglet, serial, glob, time
from pyglet.window import mouse

pyglet.resource.path = ['img']
pyglet.resource.reindex()

class PyPL_GUI():
	
	def __init__(self,
		bg_img = 'bg_img.png',
		port = '/dev/tty.usbmodem*',
		timeout = 0.1,
		):
		self.bg_img = pyglet.resource.image(bg_img)
		self.window = pyglet.window.Window(width = self.bg_img.width, height = self.bg_img.height)
		self.board = serial.Serial(glob.glob(port)[0], timeout = timeout)
		self.rbuf = b''
		self.board.write(b'\r')
		self.instructions = []
		self.population = []
		self.state = {}

		@self.window.event
		def on_draw():
			self.window.clear()
			self.bg_img.blit(0, 0)
			for w in self.population:
				w.draw()

		@self.window.event
		def on_mouse_release(x, y, button, modifiers):
			if button == mouse.LEFT:
				for w in self.population[::-1]:
					if w.in_active_area(x, y):
						w.activate()
						break
	
	def read(self, dt):

		# read instructions from serial
		while self.board.inWaiting():
			self.rbuf += self.board.read()
		if self.rbuf:
			self.instructions += self.rbuf.split(b'\r')
			self.rbuf = self.instructions.pop()

		# process instructions
		while self.instructions:
			i = self.instructions.pop(0).decode().split(';')
			if i[0] == 'status':
				for j in i[1:]:
					k,v = j.split('=')
					if v[0] == 'b':
						self.state[k] = bool(int(v[1:]))
					elif v[0] == 'f':
						self.state[k] = float(v[1:])
					elif v[0] == 's':
						self.state[k] = v[1:]
				print(self.state, end = '\r')

	def send(self, txt):
		self.board.write(txt.encode())

	def start(self):
		pyglet.clock.schedule_interval(self.read, 0.05)
		pyglet.app.run()

	
class Widget():
	
	def __init__(self):
		self.visible = True

	def in_active_area(self, x, y):
		if self.visible and 'active_area_type' in dir(self):
			if self.active_area_type == 'circle':
				return ((x - self.x)**2 + (y - self.y)**2) < self.active_area_radius**2
			elif self.active_area_type == 'rectangle':
				return (
					(x - self.x) > self.active_area_rectangle[0]
					and (x - self.x) < self.active_area_rectangle[1]
					and (y - self.y) > self.active_area_rectangle[2]
					and (y - self.y) < self.active_area_rectangle[3]
					)
		return False


class Text_Widget(Widget):
	
	def __init__(self,
		pypl_instance, x, y, uid,
		font_name = 'Menlo',
		font_size = 24,
		anchor_x = 'center',
		anchor_y = 'center',
		color = (0, 0, 0, 255),
		avg = 1,
		fmtstr = '{:+03.1f}',
		):

		Widget.__init__(self)
		self.uid = uid
		self.avg = avg
		self.fmtstr = fmtstr
		self.parent = pypl_instance
		self.state = [0]*self.avg
		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2

		self.label = pyglet.text.Label(
			'',
			font_name = font_name,
			font_size = font_size,
			color = color,
			x = self.x,
			y = self.y,
			anchor_x = anchor_x,
			anchor_y = anchor_y,
			)
		self.parent.population.append(self)
	
	def draw(self):
		if self.avg > 1:
			self.state = self.state[1:] + [self.parent.state[self.uid]]
			self.label.text = self.fmtstr.format(sum(self.state) / self.avg)
		else:
			self.state = self.parent.state[self.uid]
			self.label.text = self.fmtstr.format(self.state)
		self.label.draw()


class Toggle_Widget(Widget):
	
	def __init__(self,
		pypl_instance, x, y, uid,
		on_icon = 'valve_open.png',
		off_icon = 'valve_closed.png',
		):

		Widget.__init__(self)

		self.state = False
		self.uid = uid
		self.parent = pypl_instance

		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2

		self.on_icon = pyglet.resource.image(on_icon)
		self.off_icon = pyglet.resource.image(off_icon)

		self.width = self.on_icon.width
		self.height = self.on_icon.height

		self.active_area_type = 'circle'
		self.active_area_radius = self.width // 2

		self.on_sprite = pyglet.sprite.Sprite(
			self.on_icon,
			x + (self.parent.window.width - self.width) // 2,
			y + (self.parent.window.height - self.height) // 2,
			)
		self.off_sprite = pyglet.sprite.Sprite(
			self.off_icon,
			x + (self.parent.window.width - self.width) // 2,
			y + (self.parent.window.height - self.height) // 2,
			)

		self.parent.population.append(self)
	
	def draw(self):
		self.state = self.parent.state[self.uid]
		if self.visible:
			if self.state:
				self.on_sprite.draw()
			else:
				self.off_sprite.draw()

	def activate(self):
		self.parent.send(f'toggle;{self.uid}\r')
	
	
if __name__ == '__main__':
	
	UI = PyPL_GUI()
	Text_Widget(UI, 0, 0, 'T1', font_size = 18, fmtstr = 'T1 = {:.2f} °C')
	Toggle_Widget(UI, -200, -150, 'V1')
	Text_Widget  (UI, -200, -280, 'V1', font_size = 14, fmtstr = 'V1 = {!s}')
	Toggle_Widget(UI,    0, -150, 'V2')
	Text_Widget  (UI,    0, -280, 'V2', font_size = 14, fmtstr = 'V2 = {!s}')
	Toggle_Widget(UI,  200, -150, 'V3')
	Text_Widget  (UI,  200, -280, 'V3', font_size = 14, fmtstr = 'V3 = {!s}')
	UI.start()