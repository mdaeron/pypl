#! /usr/bin/env python3

import pyglet, serial, glob, time, arrow, sys
from pyglet.window import mouse
from pathlib import Path
from colorama import Fore, Style
from collections import defaultdict
from numpy import log10, floor, cos, sin, pi
from scipy.interpolate import interp1d
pyglet.resource.path = ['img']
pyglet.resource.reindex()

from build_gui_elements import (
	V1_X, V1_Y,
	V2_X, V2_Y,
	V3_X, V3_Y,
	V4_X, V4_Y,
	V5_X, V5_Y,
	V6_X, V6_Y,
	V7_X, V7_Y,
	V8_X, V8_Y,
	V9_X, V9_Y,
	V10_X, V10_Y,
	V11_X, V11_Y,
	V12_X, V12_Y,
	INLET_CROSS_X, INLET_CROSS_Y,
	ACID_PUMP_X, ACID_PUMP_Y,
	TRAP_A_X, TRAP_A_Y,
	GAUGE_A_X, GAUGE_A_Y,
	TRAP_B_X, TRAP_B_Y,
	GAUGE_B_X, GAUGE_B_Y,
	GAUGE_C_X, GAUGE_C_Y,
	TRAP_C_X, TRAP_C_Y,
	VACUUM_X, VACUUM_Y,
	REACTOR_X, REACTOR_Y,
	TURBO_X, TURBO_Y,
	SCROLL_X, SCROLL_Y,
	ACID_GAUGE_X, ACID_GAUGE_Y,
	)

DEBUG = False

class DummyBoard():
	def __init__(self):
		pass

	def write(self, msg):
		pass

	def inWaiting(self):
		return False


class PyPL_GUI():
	
	def __init__(self,
		bg_img = 'bg_img.png',
		port = ['/dev/tty.usbmodem*', '/dev/ttyACM*'],
		timeout = 0.1,
		):
		self.bg_img = pyglet.resource.image(bg_img)
		self.window = pyglet.window.Window(width = self.bg_img.width, height = self.bg_img.height)
		for p in port:
			glb = glob.glob(p)
			if glb:
				self.board = serial.Serial(glb[0], timeout = timeout)
				break
		else:
			self.board = DummyBoard()
		self.rbuf = b''
		self.board.write(b'\r')
		self.instructions = []
		self.population = []
		self.state = defaultdict(lambda: 0.)
		self.start_of_timer = arrow.now()
		Path('logs/').mkdir(exist_ok  =True)
		Path('logs/bg/').mkdir(exist_ok  =True)
		Path('logs/other/').mkdir(exist_ok  =True)
		Path('logs/preplogs/').mkdir(exist_ok  =True)
		self.current_preplog = None
		self.current_other_log = None
		
		@self.window.event
		def on_draw():
			self.window.clear()
			self.bg_img.blit(0, 0)
			for w in self.population:
				if w.visible:
					w.draw()

		@self.window.event
		def on_mouse_release(x, y, button, modifiers):
			if button == mouse.LEFT:
				for w in self.population[::-1]:
					if w.in_active_area(x, y):
						w._activate(w)
						break

	def start_prep(self, subdir = 'preplogs', prefix = 'carousel_'):
		self.current_preplog = f'logs/{subdir}/{prefix}' + arrow.now().format('YYYY-MM-DD-HH[h]mm') + '.csv'

	def log(self, echo = None, subdir = 'bg', prefix = '', fields = 'T1:.2f,T2:.2f,T3:.2f,T4:.2f,P1:.4e,P2:.4e,P3:.4e,P4:.4e'):
		fields = [f.split(':') for f in fields.split(',')]
		if subdir == 'bg':
			logfile = Path(f'logs/{subdir}/{prefix}' + arrow.now().format('YYYY-MM-DD') + '.csv')
		elif subdir == 'preplogs':
			logfile = Path(self.current_preplog)
		elif subdir == 'other':
			logfile = Path(self.current_other_log)

		if logfile.exists():
			fid = open(logfile, 'a')
		else:
			fid = open(logfile, 'w')
# 			fid.write('Time,P1')
# 			fid.write('Time,X,Y,Z')
			fid.write('Time,' + ','.join([f for f, g in fields]))

		if echo is None:
			fid.write(','.join(
				[f"\n{self.state['NOW']}"] +
				['' if self.state[f] is None else f"{self.state[f]:{g}}" for f,g in fields]
				))
		else:
			fid.write(f"\n# {self.state['NOW']},{echo}")

		fid.close()
	
	def bg_log(self, t, echo = None, subdir = 'bg', prefix = ''):
		self.log(echo = echo, subdir = subdir, prefix = prefix)

	def prep_log(self, t, echo = None, subdir = 'preplogs', prefix = ''):
		self.log(echo = echo, subdir = subdir, prefix = prefix)

	def other_log(self, t, echo = None, subdir = 'other', prefix = ''):
		self.log(echo = echo, subdir = subdir, prefix = prefix)

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
					elif v[0] == 'n':
						self.state[k] = None
# 				print(self.state, end = '\r')
			elif i[0] == 'echo':
				for j in i[1:]:
					print(j)
			elif i[0] == 'echolog':
				for j in i[1:]:
					print(j)
					self.prep_log(0, echo = j)
			elif i[0] == 'newline':
				print('')
			elif i[0] == 'clearline':
				sys.stdout.write('\033[F')
			elif i[0] == 'timestamp':
				t = arrow.now()
				dt = (t - self.start_of_timer).total_seconds()
				print(f'{t.format("YYYY-MM-DD HH:mm:ss")} {Fore.GREEN}[ {dt//60:02.0f}:{dt % 60:02.0f} ]{Style.RESET_ALL} ', end = '')
			elif i[0] == 'zero_clock':
				self.start_of_timer = arrow.now()
			elif i[0] == 'end_prep':
				pyglet.clock.unschedule(self.prep_log)
				self.current_preplog = None
			elif i[0] == 'start_prep':
				self.start_prep()
				pyglet.clock.schedule_interval(self.prep_log, .5)


	def send(self, txt):
		print(txt[:-1])
		self.board.write(txt.encode())

	def set_rtc(self):
		now = arrow.now()
		self.send('@pypl.set_rtc((%s,%d,%s))\r' % (now.format('YYYY,MM,DD'), (now.weekday() - 1) % 7 + 1, now.format('HH,mm,ss,255')))

	def start(self):
		self.set_rtc()
		pyglet.clock.schedule_interval(self.bg_log, 1)
		pyglet.clock.schedule_interval(self.relay, 2)
		pyglet.clock.schedule_interval(self.read, 0.05)
		pyglet.app.run()

	def start_other_log(self, subdir = 'other', prefix = ''):
		self.current_other_log = f'logs/{subdir}/{prefix}' + arrow.now().format('YYYY-MM-DD-HH[h]mm') + '.csv'
		pyglet.clock.schedule_interval(self.other_log, .5)

	def stop_other_log(self):
		pyglet.clock.unschedule(self.other_log)
		self.current_other_log = None

	def relay(self, dt, filename = '.board_input'):
		try:
			with open(filename, 'r') as f:
				for l in f.readlines():
					if len(l) and l[0] == '@' and l[-1] == '\n':
						self.send(l[:-1]+'\r')
		except FileNotFoundError:
			pass
		with open(filename, 'w') as f:
			f.write('')



class Widget():
	
	def __init__(self):
		self.visible = True
		self._refresh = lambda x: None
		self._activate = lambda x: None

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

	def refresh(self, fun):
		self._refresh = fun

	def activate(self, fun):
		self._activate = fun

class TextWidget(Widget):
	def __init__(self,
		pypl_instance,
		x, y,
		label = '',
		font_name = 'Menlo',
		font_size = 24,
		bold = False,
		anchor_x = 'center',
		anchor_y = 'center',
		align = 'center',
		color = (0, 0, 0, 255),
		):
		Widget.__init__(self)
		self.parent = pypl_instance
		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2

		self.label = pyglet.text.Label(
			label,
			font_name = font_name,
			font_size = font_size,
			bold = bold,
			color = color,
			x = self.x,
			y = self.y,
			anchor_x = anchor_x,
			anchor_y = anchor_y,
			multiline = True,
			align = align,
			width = 1000,
			)
		self.parent.population.append(self)

	def draw(self):
		self._refresh(self)
		self.label.draw()

class IconWidget(Widget):
	
	def __init__(self,
		pypl_instance,
		x, y,
		icon = '',
		):

		Widget.__init__(self)
		self.parent = pypl_instance
		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2
		self.icon = pyglet.resource.image(icon)

		self.width = self.icon.width
		self.height = self.icon.height
		self.icon.anchor_x = self.width // 2
		self.icon.anchor_y = self.height // 2
		self.sprite = pyglet.sprite.Sprite(self.icon, self.x, self.y)
		self.parent.population.append(self)

	def draw(self):
		self._refresh(self)
		self.sprite.draw()

class ToggleWidget(Widget):
	
	def __init__(self,
		pypl_instance,
		x, y,
		icon_on = '',
		icon_off = '',
		state = False,
		):

		Widget.__init__(self)
		self.parent = pypl_instance
		self.x = x + (self.parent.window.width) // 2
		self.y = y + (self.parent.window.height) // 2
		self.icon_on = pyglet.resource.image(icon_on)
		self.icon_off = pyglet.resource.image(icon_off)
		self.state = state

		self.width = self.icon_on.width
		self.height = self.icon_on.height
		self.icon_on.anchor_x = self.width // 2
		self.icon_on.anchor_y = self.height // 2
		self.icon_off.anchor_x = self.width // 2
		self.icon_off.anchor_y = self.height // 2
		self.sprite_on = pyglet.sprite.Sprite(self.icon_on, self.x, self.y)
		self.sprite_off = pyglet.sprite.Sprite(self.icon_off, self.x, self.y)
		self.parent.population.append(self)

	def draw(self):
		self._refresh(self)
		if self.state:
			self.sprite_on.draw()
		else:
			self.sprite_off.draw()


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
			try:
				self.label.text = self.fmtstr.format(sum(self.state) / self.avg)
			except TypeError:
				self.label.text = '#'
		else:
			self.state = self.parent.state[self.uid]
			try:
				self.label.text = self.fmtstr.format(self.state)
			except TypeError:
				self.label.text = '#'
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
		scale = 'lin',
		):

		Widget.__init__(self)
		self.uid = uid
		self.avg = avg
		self.scale = scale
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
			if self.scale == 'log':
				self.sprite.rotation = self._angle(log10(self.state))
				self.sprite.opacity = self._alpha(log10(self.state))*255
			else:
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
	

class Command_Widget(Widget):
	
	def __init__(self,
		pypl_instance, x, y, f_start, f_stop,
		on_icon = 'logger_stop.png',
		off_icon = 'logger_start.png',
		):

		Widget.__init__(self)

		self.state = False
		self.parent = pypl_instance
		self.f_start = f_start
		self.f_stop = f_stop

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
			self.f_start()
		else:
			self.f_stop()
	

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


class Sender_Widget(Widget):
	
	def __init__(self, pypl_instance, x, y, icon, instruction, alpha = 1):

		Widget.__init__(self)

		self.visible = True
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
		if self.visible:
			self.sprite.draw()

	def activate(self):
		self.parent.send(f'{self.instruction}\r')

def Valve(UI, name, x, y, label = None, label_pos = '-90'):
	if label is None:
		label = name[1:]
	V = ToggleWidget(UI, x, y, 'valve_open.png', 'valve_closed.png')
	V.name = name[:]
	V.active_area_type = 'circle'
	V.active_area_radius = V.width // 2
	@V.refresh
	def valve_refresh(self):
		self.state = self.parent.state[self.name]
	@V.activate
	def valve_activate(self):
		self.parent.send(f'@pypl.{self.name}.toggle()\r')	
	TextWidget(UI, x+40*cos(label_pos/180*pi), y+40*sin(label_pos/180*pi), font_name = 'Helvetica', font_size = 14, color = (153,153,153,255), label = label, bold = True)
	return V

def Trap(UI, name, i, x, y, Tlimits = [-170, -90, -70, 0, 30, 40], shape = 'L', label = None):
	if label is None:
		label = name[-1]
	T = f'T{i}'
	TS = f'TS{i}'
	cPWM = f'cPWM{i}'
	hPWM = f'hPWM{i}'
	T_Background = IconWidget(UI, x, y, icon = f'trap_{shape}_white.png')
	T_BakeColor = IconWidget(UI, x, y, icon = f'trap_{shape}_orange.png')
	T_ThawColor = IconWidget(UI, x, y, icon = f'trap_{shape}_magenta.png')
	T_FreezeColor = IconWidget(UI, x, y, icon = f'trap_{shape}_cyan.png')

	alpha_bake = interp1d([-1e3, Tlimits[-2], Tlimits[-1], 1e3], [0,0,255,255])
	alpha_thaw = interp1d([-1e3, Tlimits[0], Tlimits[1], Tlimits[2], Tlimits[3], 1e3], [0,0,255,255,0,0])
	alpha_freeze = interp1d([-1e3, Tlimits[0], Tlimits[1], 1e3], [255,255,0,0])

	@T_BakeColor.refresh
	def foo(self):
		self.sprite.opacity = int(alpha_bake(self.parent.state[T]))

	@T_ThawColor.refresh
	def foo(self):
		self.sprite.opacity = int(alpha_thaw(self.parent.state[T]))

	@T_FreezeColor.refresh
	def foo(self):
		self.sprite.opacity = int(alpha_freeze(self.parent.state[T]))

	T_Text = TextWidget(UI, x, y-30, font_name = 'Helvetica', font_size = 14, color = (0,0,0,255))
	@T_Text.refresh
	def foo(self):
		self.label.text = '%+.0f °C' % self.parent.state[T]

	TS_freeze_button_Background = IconWidget(UI, x-35, y-70, icon = 'button_snowflake_24_white.png')
	TS_freeze_button_Background.active_area_type = 'rectangle'
	TS_freeze_button_Background.active_area_rectangle = [-15, 15, -15, 15]
	@TS_freeze_button_Background.activate
	def foo(self):
		if self.parent.state[TS] == -200:
			self.parent.send(f'@pypl.{TS}.stop()\r')
		else:
			self.parent.send(f'@pypl.{TS}.start(-200)\r')
	TS_freeze_button_Color = IconWidget(UI, x-35, y-70, icon = 'button_snowflake_24_cyan.png')
	@TS_freeze_button_Color.refresh
	def foo(self):
		if self.parent.state[TS] is None or self.parent.state[TS] > -100:
			self.sprite.opacity = 0
		else:
			self.sprite.opacity = 255 if self.parent.state[cPWM] else 127

	TS_thaw_button_Background = IconWidget(UI, x, y-70, icon = 'button_snowflake_16_white.png')
	TS_thaw_button_Background.active_area_type = 'rectangle'
	TS_thaw_button_Background.active_area_rectangle = [-15, 15, -15, 15]
	@TS_thaw_button_Background.activate
	def foo(self):
		if self.parent.state[TS] == -80:
			self.parent.send(f'@pypl.{TS}.stop()\r')
		else:
			self.parent.send(f'@pypl.{TS}.start(-80)\r')
	TS_thaw_button_Color = IconWidget(UI, x, y-70, icon = 'button_snowflake_16_magenta.png')
	@TS_thaw_button_Color.refresh
	def foo(self):
		if self.parent.state[TS] is None or self.parent.state[TS] < -100 or self.parent.state[TS] > 0:
			self.sprite.opacity = 0
		else:
			self.sprite.opacity = 255 if self.parent.state[cPWM] else 127

	TS_bake_button_Background = IconWidget(UI, x+35, y-70, icon = 'button_hot_24_white.png')
	TS_bake_button_Background.active_area_type = 'rectangle'
	TS_bake_button_Background.active_area_rectangle = [-15, 15, -15, 15]
	@TS_bake_button_Background.activate
	def foo(self):
		if self.parent.state[TS] == 50:
			self.parent.send(f'@pypl.{TS}.stop()\r')
		else:
			self.parent.send(f'@pypl.{TS}.start(40)\r')
		
	TS_bake_button_Color = IconWidget(UI, x+35, y-70, icon = 'button_hot_24_orange.png')
	@TS_bake_button_Color.refresh
	def foo(self):
		if self.parent.state[TS] is None or self.parent.state[TS] < 20:
			self.sprite.opacity = 0
		else:
			self.sprite.opacity = 255 if self.parent.state[hPWM] else 127


	TS_Text = TextWidget(UI, x, y-100, font_name = 'Helvetica', font_size = 10, color = (0,0,0,255))
	@TS_Text.refresh
	def foo(self):
		self.label.text = '' if self.parent.state[TS] is None else 'Target: %+g °C' % self.parent.state[TS]

	TextWidget(UI, x-25, y+25, font_name = 'Helvetica', font_size = 18, color = (0,0,0,51), label = label, bold = True)

def Gauge(UI, name, P, x, y):
	P_Background = IconWidget(UI,x, y, icon = 'gauge_white.png')
	P_Color = IconWidget(UI, x, y, icon = 'gauge_yellow.png')
	@P_Color.refresh
	def foo(self):
		if self.parent.state[P] is None:
# 			self.parent.state[P] = 0.02733
			return None
		if self.parent.state[P] > 0:
# 			self.parent.state[P] = 0.02733
			self.sprite.opacity = int((min(3, max(-5, log10(self.parent.state[P])))+5)/8*255)
		else:
			self.sprite.opacity = 0

	P_Text = TextWidget(UI, x, y, font_name = 'Helvetica', font_size = 14, color = (0,0,0,255))
	@P_Text.refresh
	def foo(self):
		if self.parent.state[P] is None:
			return None
		if self.parent.state[P] > 0:
			x = self.parent.state[P]
			y = int(floor(log10(x)))
			if y > -2:
				n = 3-y
				self.label.text = f'{x:.{n}f}\nmbar'
	# 			self.label.text = f'{x:g}\nmbar'
			else:
				self.label.text = f'{x:.5f}\nmbar'
	# 			z = x / 10**y
	# 			n = min(y + 5, 3)
	# 			self.label.text = f'{z:.{n}f} e{y}\nmbar'
		else:
				self.label.text = ''


def CancellableCommand(UI, x, y, name):

	cmd = IconWidget(UI, x, y, icon = f'command_{name}.png')
	cmd.active_area_type = 'rectangle'
	cmd.active_area_rectangle = (-75, 75, -15, 15)
	@cmd.activate
	def cmd_activate(self):
		self.parent.send(f'@pypl.run_{name}()\r')
		self.visible = False
		stop_cmd.visible = True

	stop_cmd = IconWidget(UI, x, y, icon = 'command_stop.png')
	stop_cmd.visible = False
	stop_cmd.active_area_type = 'rectangle'
	stop_cmd.active_area_rectangle = (-75, 75, -15, 15)
	@stop_cmd.activate
	def stop_cmd_activate(self):
# 		self.visible = False
		confirm_stop.visible = True
		cancel_stop.visible = True

	confirm_stop = IconWidget(UI, 0, -60, icon = 'command_stop_for_real.png')
# 	confirm_stop.sprite.opacity = 230
	confirm_stop.visible = False
	confirm_stop.active_area_type = 'rectangle'
	confirm_stop.active_area_rectangle = (-250, 250, -50, 50)
	@confirm_stop.activate
	def confirm_stop_activate(self):
		self.parent.send(f'@pypl.task_{name}.cancel()\r')
		self.visible = False
		stop_cmd.visible = False
		cmd.visible = True
		cancel_stop.visible = False

	cancel_stop = IconWidget(UI, 0, 60, icon = 'command_no_never_mind.png')
# 	cancel_stop.sprite.opacity = 230
	cancel_stop.visible = False
	cancel_stop.active_area_type = 'rectangle'
	cancel_stop.active_area_rectangle = (-250, 250, -50, 50)
	@cancel_stop.activate
	def cancel_stop_activate(self):
		self.visible = False
		confirm_stop.visible = False


if __name__ == '__main__':
		
	UI = PyPL_GUI()

	traps = {name: Trap(UI, name, TS, x, y,
# 		Tlimits = [22, 24, 26, 28, 30, 40],
		shape = shape) for name, TS, x, y, shape in [
		('Trap_A', '1', TRAP_A_X, TRAP_A_Y, 'L'),
		('Trap_B', '2', TRAP_B_X, TRAP_B_Y, 'L'),
		('Trap_C', '3', TRAP_C_X, TRAP_C_Y, 'I'),
		]}

	pumps_vac = IconWidget(UI, VACUUM_X, (3*TURBO_Y + VACUUM_Y)//4, icon = 'vacline_pumps.png')
	top_vac = IconWidget(UI, (INLET_CROSS_X + SCROLL_X)//2, (VACUUM_Y + V5_Y)//2, icon = 'vacline_top.png')
	trapA_vac = IconWidget(UI, (V1_X + V4_X)//2, (V3_Y + V4_Y)//2, icon = 'vacline_trapA.png')
	V456_vac = IconWidget(UI, (V4_X + V5_X)//2, (V5_Y + V6_Y)//2, icon = 'vacline_V456.png')
	trapB_vac = IconWidget(UI, (V6_X + V7_X)//2, (V6_Y + V7_Y)//2, icon = 'vacline_trapB.png')
	trapC_vac = IconWidget(UI, (V7_X + V8_X)//2, (V8_Y + TRAP_C_Y)//2, icon = 'vacline_trapC.png')
	crds_vac = IconWidget(UI, V8_X, (V8_Y+TRAP_B_Y+77)//2, icon = 'vacline_crds.png')
	reactor_vac = IconWidget(UI, REACTOR_X, (REACTOR_Y+V12_Y)//2, icon = 'vacline_reactor.png')

	pumped_opacity = 255

	@top_vac.refresh
	def top_vac_refresh(self):
		if self.parent.state['V10'] or self.parent.state['V11']:
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	@trapA_vac.refresh
	def trapA_vac_refresh(self):
		if (
			(self.parent.state['V3'] and top_vac.sprite.opacity == pumped_opacity)
			or (self.parent.state['V4'] and self.parent.state['V5'] and top_vac.sprite.opacity == pumped_opacity)
			):
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	@V456_vac.refresh
	def trapA_vac_refresh(self):
		if (
			(self.parent.state['V5'] and top_vac.sprite.opacity == pumped_opacity)
			or (self.parent.state['V4'] and self.parent.state['V3'] and top_vac.sprite.opacity == pumped_opacity)
			):
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	@trapB_vac.refresh
	def trapB_vac_refresh(self):
		if (
			(self.parent.state['V6'] and V456_vac.sprite.opacity == pumped_opacity)
			):
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	@trapC_vac.refresh
	def trapC_vac_refresh(self):
		if (
			(self.parent.state['V7'] and trapB_vac.sprite.opacity == pumped_opacity)
			):
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	@crds_vac.refresh
	def crds_vac_refresh(self):
		if (
			(self.parent.state['V8'] and trapC_vac.sprite.opacity == pumped_opacity)
			):
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	@reactor_vac.refresh
	def reactor_vac_refresh(self):
		if (
			(self.parent.state['V1'] and trapA_vac.sprite.opacity == pumped_opacity)
			):
			self.sprite.opacity = pumped_opacity
		else:
			self.sprite.opacity = 255 - pumped_opacity

	gauges = {name: Gauge(UI, name, P, x, y) for name, P, x, y in [
		('Gauge_A', 'P1', GAUGE_A_X, GAUGE_A_Y),
		('Gauge_B', 'P2', GAUGE_B_X, GAUGE_B_Y),
		('Gauge_C', 'P3', GAUGE_C_X, GAUGE_C_Y),
		('Gauge_D', 'P4', ACID_GAUGE_X, ACID_GAUGE_Y),
		]}

	valves = {v: Valve(UI, v, x, y, label_pos = label_pos) for v, x, y, label_pos in [
		('V1', V1_X, V1_Y, -90),
		('V2', V2_X, V2_Y, 45),
		('V3', V3_X, V3_Y, 135),
		('V4', V4_X, V4_Y, -135),
		('V5', V5_X, V5_Y, 0),
		('V6', V6_X, V6_Y, -45),
		('V7', V7_X, V7_Y, -135),
		('V8', V8_X, V8_Y, 0),
		('V9', V9_X, V9_Y, 90),
		('V10', V10_X, V10_Y, 135),
		('V11', V11_X, V11_Y, 45),
		('V12', V12_X, V12_Y, 90),
		]}

	reactor_cmd = {
		'bwd': IconWidget(UI, REACTOR_X-20, REACTOR_Y-140, icon = 'button_bwd_20_white.png'),
		'ubwd': IconWidget(UI, REACTOR_X-20, REACTOR_Y-100, icon = 'button_ubwd_12_white.png'),
		'ufwd': IconWidget(UI, REACTOR_X+20, REACTOR_Y-100, icon = 'button_ufwd_12_white.png'),
		'fwd': IconWidget(UI, REACTOR_X+20, REACTOR_Y-140, icon = 'button_fwd_20_white.png'),
		}	

	n = reactor_cmd['bwd']
	n.active_area_type = 'rectangle'
	n.active_area_rectangle = [-15, 15, -15, 15]
	@n.activate
	def foo(self):
		self.parent.send(f'@pypl.stepper.bwd()\r')

	n = reactor_cmd['ubwd']
	n.active_area_type = 'rectangle'
	n.active_area_rectangle = [-15, 15, -15, 15]
	@n.activate
	def foo(self):
		self.parent.send(f'@pypl.stepper.microbwd()\r')

	n = reactor_cmd['ufwd']
	n.active_area_type = 'rectangle'
	n.active_area_rectangle = [-15, 15, -15, 15]
	@n.activate
	def foo(self):
		self.parent.send(f'@pypl.stepper.microfwd()\r')

	n = reactor_cmd['fwd']
	n.active_area_type = 'rectangle'
	n.active_area_rectangle = [-15, 15, -15, 15]
	@n.activate
	def foo(self):
		self.parent.send(f'@pypl.stepper.fwd()\r')

	IconWidget(UI, REACTOR_X, REACTOR_Y, icon = 'acid_130.png')

	turbo_bg = IconWidget(UI, TURBO_X, TURBO_Y, icon = 'pump_white.png')
	turbo_bg.active_area_type = 'circle'
	turbo_bg.active_area_radius = 50
	@turbo_bg.activate
	def turbo_bg_activate(self):
		self.parent.send(f'@pypl.V9.open()\r')
		self.parent.send(f'@pypl.V10.open()\r')
		self.parent.send(f'@pypl.V11.close()\r')

	turbo_ok = IconWidget(UI, TURBO_X, TURBO_Y, icon = 'pump_green.png')
	@turbo_ok.refresh
	def turbo_ok_refresh(self):
		if self.parent.state['V10'] and self.parent.state['V9'] and not self.parent.state['V11']:
			self.sprite.opacity = 255
		else:
			self.sprite.opacity = 0

	turbo_pb = IconWidget(UI, TURBO_X, TURBO_Y, icon = 'pump_red.png')
	@turbo_pb.refresh
	def turbo_ok_refresh(self):
		if (
			(self.parent.state['V10'] and not self.parent.state['V9'])
			or
			(self.parent.state['V10'] and self.parent.state['V11'])
			):
			self.sprite.opacity = 255
		else:
			self.sprite.opacity = 0
	

	

	scroll_bg = IconWidget(UI, SCROLL_X, SCROLL_Y, icon = 'pump_white.png')
	scroll_bg.active_area_type = 'circle'
	scroll_bg.active_area_radius = 50
	@scroll_bg.activate
	def scroll_bg_activate(self):
		self.parent.send(f'@pypl.V9.close()\r')
		self.parent.send(f'@pypl.V10.close()\r')
		self.parent.send(f'@pypl.V11.open()\r')

	scroll_ok = IconWidget(UI, SCROLL_X, SCROLL_Y, icon = 'pump_yellow.png')
	@scroll_ok.refresh
	def scroll_ok_refresh(self):
		if self.parent.state['V11'] and not self.parent.state['V10']:
			self.sprite.opacity = 255
		else:
			self.sprite.opacity = 0

	scroll_pb = IconWidget(UI, SCROLL_X, SCROLL_Y, icon = 'pump_red.png')
	@scroll_pb.refresh
	def scroll_ok_refresh(self):
		if self.parent.state['V10'] and self.parent.state['V11']:
			self.sprite.opacity = 255
		else:
			self.sprite.opacity = 0


	acid_pump_bg = IconWidget(UI, ACID_PUMP_X, ACID_PUMP_Y, icon = 'pump_white.png')

	TextWidget(UI, ACID_PUMP_X, ACID_PUMP_Y, font_name = 'Helvetica', font_size = 14, color = (0,0,0,255), label = 'acid\npump', bold = True)
	TextWidget(UI, TURBO_X, TURBO_Y, font_name = 'Helvetica', font_size = 14, color = (0,0,0,255), label = 'turbo\npump', bold = True)
	TextWidget(UI, SCROLL_X, SCROLL_Y, font_name = 'Helvetica', font_size = 14, color = (0,0,0,255), label = 'scroll\npump', bold = True)

	Tacid = TextWidget(UI, REACTOR_X, REACTOR_Y+55, font_name = 'Helvetica', font_size = 12, color = (0,0,0,255), label = '', bold = True)
	@Tacid.refresh
	def Tacid_refresh(self):
		self.label.text = '%.0f °C' % self.parent.state['T4']

	X, Y = 385, -350

	standby_cmd = IconWidget(UI, X, Y, icon = 'command_standby.png')
	standby_cmd.active_area_type = 'rectangle'
	standby_cmd.active_area_rectangle = (-75, 75, -50, 50)
	@standby_cmd.activate
	def standby_cmd_activate(self):
		self.parent.send(f'@pypl.standby()\r')

	Y += 40
	CancellableCommand(UI, X, Y, 'carb')

	Y += 40
	CancellableCommand(UI, X, Y, 'CO2')

	Y += 40
	CancellableCommand(UI, X, Y, 'transfer')
	
	if DEBUG:
		debug = TextWidget(UI, -500, 350, font_name = 'Helvetica', font_size = 12, color = (255,0,0,255), label = '')
		@debug.refresh
		def foo(self):
			self.label.text = self.parent.state['DEBUG']

# 	Icon_Widget(UI, -300, -80, 'P1', x_min = -5, x_max = 3, angle_min = -45, angle_max = 45, scale = 'log', icon = 'needle_line.png')
# 
# 	Icon_Widget(UI, -400, -100, 'T3', alpha_min = 1, alpha_max = 1, icon = 'tepid_box.png')
# 	Icon_Widget(UI, -400, -100, 'T3', x_min = 25.2, x_max = 27, alpha_min = 0, alpha_max = 1, icon = 'hot_box.png')
# 	Icon_Widget(UI, -400, -100, 'T3', x_min = 24.8, x_max = 23, alpha_min = 0, alpha_max = 1, icon = 'cold_box.png')
# 
# # 	Text_Widget(UI, 0, 300, 'P1', font_size = 18, fmtstr = 'P1 = {:.4e}')
# # 	Text_Widget(UI, 0, 260, 'T2', font_size = 18, fmtstr = 'PT1000 = {:.2f} °C')
# 	Text_Widget(UI, -400, -150, 'T3', font_size = 10, fmtstr = '{:+.0f} °C')
# 	Text_Widget(UI, -300, 0, 'P1', font_size = 10, fmtstr = '{:g} mbar')
# # 	Icon_Widget(UI, 0, 100, 'T1', x_min = 19, x_max = 23, angle_min = -45, angle_max = 45)
# 
# 	Toggle_Widget(UI, -450, 200, 'V1')
# 	Toggle_Widget(UI, -350, 200, 'V2')
# 	Toggle_Widget(UI, -400, 250, 'V3')
# 	Toggle_Widget(UI, -200, -100, 'V4')
# 	Text_Widget  (UI, -200,  -60, 'V1', font_size = 14, fmtstr = 'V1 = {!s}')
# 	Toggle_Widget(UI,    0, -150, 'V2')
# 	Text_Widget  (UI,    0,  -60, 'V2', font_size = 14, fmtstr = 'V2 = {!s}')
# 	Toggle_Widget(UI,  200, -150, 'V3')
# 	Text_Widget  (UI,  200,  -60, 'V3', font_size = 14, fmtstr = 'V3 = {!s}')
# 
# 	Command_Widget(UI,  0, 100, f_start = UI.start_other_log, f_stop = UI.stop_other_log)
# 
# 	Dialog_Widget(UI, 0, -300, 'start_blink_dialog', 'button_start.png', instruction = 'start_blink')
# 	Dialog_Widget(UI, 0, -300, 'stop_blink_dialog', 'button_stop.png', instruction = 'stop_blink')
# 	Dialog_Widget(UI, 0,   50, 'confirm_stop_blink_dialog', 'button_abort.png', instruction = 'confirm_stop_blink')
# 	Dialog_Widget(UI, 0,  -50, 'undo_stop_blink_dialog', 'button_undo.png', instruction = 'undo_stop_blink')
# 	
# 	Sender_Widget(UI, 100, -300, 'button_fwd.png', 'stepper;fwd')
# 	Sender_Widget(UI, -100, -300, 'button_bwd.png', 'stepper;bwd')

	UI.start()