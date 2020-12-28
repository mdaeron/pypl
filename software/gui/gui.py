#! /usr/bin/env python3

import pyglet, serial, glob, time, arrow, sys
from pyglet.window import mouse
from pathlib import Path
from colorama import Fore, Style

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
		self.start_of_timer = arrow.utcnow()

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

	def log(self, dt):
		self.logfile = Path('logs/'+arrow.now().format('YYYY-MM-DD') + '.csv')
		if self.logfile.exists():
			fid = open(self.logfile, 'a')
		else:
			self.logfile.parent.mkdir(exist_ok  =True)
			fid = open(self.logfile, 'w')
			fid.write('Time,T1,T2')
		fid.write(f"\n{self.state['NOW']},{self.state['T1']:.2f},{self.state['T2']:.2f}")
		fid.close()
	
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
			elif i[0] == 'echo':
				for j in i[1:]:
					print(j)
			elif i[0] == 'newline':
				print('')
			elif i[0] == 'clearline':
				sys.stdout.write('\033[F')
			elif i[0] == 'timestamp':
				t = arrow.utcnow()
				dt = (t - self.start_of_timer).total_seconds()
				print(f'{t.format("YYYY-MM-DD HH:mm:ss")} {Fore.GREEN}[ {dt//60:02.0f}:{dt % 60:02.0f} ]{Style.RESET_ALL} ', end = '')
			elif i[0] == 'zero_clock':
				self.start_of_timer = arrow.utcnow()

	def send(self, txt):
		self.board.write(txt.encode())

	def set_rtc(self):
		now = arrow.now()
		self.send(f'set_rtc;%s;%d;%s' % (now.format('YYYY;MM;DD'), (now.weekday() - 1) % 7 + 1, now.format('hh;mm;ss;255\r')))

	def start(self):
		self.set_rtc()
		pyglet.clock.schedule_interval(self.read, 0.05)
		pyglet.clock.schedule_interval(self.log, 1)
		pyglet.app.run()
	
	def start_log(self, uid):
		print(f'start log {uid}')

	def stop_log(self, uid):
		print(f'stop log {uid}')

	
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


class Icon_Widget(Widget):
	
	def __init__(self,
		pypl_instance, x, y, uid,
		icon = 'needle.png',
		avg = 1,
		x_min = 0,
		x_max = 1,
		angle_min = 0,
		angle_max = 0,
		alpha_min = 1,
		alpha_max = 1,
		):

		Widget.__init__(self)
		self.uid = uid
		self.avg = avg
		self.parent = pypl_instance
		self.state = [0]*self.avg
		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2
		self.icon = pyglet.resource.image(icon)
		self.angle_min, self.angle_max, self.alpha_min, self.alpha_max = angle_min, angle_max, alpha_min, alpha_max
		self.A = (angle_max - angle_min) / (x_max - x_min)
		self.B = angle_max - x_max * self.A
		self.C = (alpha_max - alpha_min) / (x_max - x_min)
		self.D = alpha_max - x_max * self.C

		self.width = self.icon.width
		self.height = self.icon.height
		self.icon.anchor_x = self.width // 2
		self.icon.anchor_y = self.height // 2
		self.sprite = pyglet.sprite.Sprite(self.icon, self.x, self.y)
		self.parent.population.append(self)
		
	def _angle(self, x):
		return max(min(self.A * x + self.B, self.angle_max), self.angle_min)

	def _alpha(self, x):
		return max(min(self.C * x + self.D, self.alpha_max), self.alpha_min)
	
	def draw(self):
		if self.avg > 1:
			self.state = self.state[1:] + [self.parent.state[self.uid]]
			self.sprite.rotation = self._angle(sum(self.state) / self.avg)
			self.sprite.opacity = (self._alpha(sum(self.state) / self.avg))*255
		else:
			self.state = self.parent.state[self.uid]
			self.sprite.rotation = self._angle(self.state)
			self.sprite.opacity = self._alpha(self.state)*255
		self.sprite.draw()


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
	

class Logger_Widget(Widget):
	
	def __init__(self,
		pypl_instance, x, y, uid,
		on_icon = 'logger_stop.png',
		off_icon = 'logger_start.png',
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
		if self.visible:
			if self.state:
				self.on_sprite.draw()
			else:
				self.off_sprite.draw()

	def activate(self):
		self.state = not self.state
		if self.state:
			self.parent.start_log(self.uid)
		else:
			self.parent.stop_log(self.uid)
	

class Dialog_Widget(Widget):
	
	def __init__(self, pypl_instance, x, y, uid, icon, instruction, alpha = 1):

		Widget.__init__(self)

		self.visible = False
		self.uid = uid
		self.parent = pypl_instance
		self.instruction = instruction
		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2

		self.icon = pyglet.resource.image(icon)

		self.width = self.icon.width
		self.height = self.icon.height

		self.active_area_type = 'rectangle'
		self.active_area_rectangle = (-self.width//2, self.width//2, -self.height//2, self.height//2)

		self.sprite = pyglet.sprite.Sprite(
			self.icon,
			x + (self.parent.window.width - self.width) // 2,
			y + (self.parent.window.height - self.height) // 2,
			)
		self.sprite.opacity = alpha * 255

		self.parent.population.append(self)
	
	def draw(self):
		self.visible = self.parent.state[self.uid]
		if self.visible:
			self.sprite.draw()

	def activate(self):
		self.parent.send(f'{self.instruction}\r')
	
if __name__ == '__main__':
	
	UI = PyPL_GUI()
	Text_Widget(UI, 0, 220, 'T1', font_size = 18, fmtstr = 'T1 = {:.2f} °C')
	Icon_Widget(UI, 0, 100, 'T1', x_min = 19, x_max = 23, angle_min = -45, angle_max = 45)
# 	Toggle_Widget(UI, -200, -150, 'V1')
# 	Text_Widget  (UI, -200,  -60, 'V1', font_size = 14, fmtstr = 'V1 = {!s}')
# 	Toggle_Widget(UI,    0, -150, 'V2')
# 	Text_Widget  (UI,    0,  -60, 'V2', font_size = 14, fmtstr = 'V2 = {!s}')
# 	Toggle_Widget(UI,  200, -150, 'V3')
# 	Text_Widget  (UI,  200,  -60, 'V3', font_size = 14, fmtstr = 'V3 = {!s}')

	Dialog_Widget(UI, 0, -300, 'start_blink_dialog', 'button_start.png', instruction = 'start_blink')
	Dialog_Widget(UI, 0, -300, 'stop_blink_dialog', 'button_stop.png', instruction = 'stop_blink')
	Dialog_Widget(UI, 0,   50, 'confirm_stop_blink_dialog', 'button_abort.png', instruction = 'confirm_stop_blink')
	Dialog_Widget(UI, 0,  -50, 'undo_stop_blink_dialog', 'button_undo.png', instruction = 'undo_stop_blink')

	Logger_Widget(UI,  0, 100, 'T1')

	UI.start()