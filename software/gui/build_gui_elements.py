#! /usr/bin/env python3

from matplotlib.patches import *
from pylab import *
from numpy import random as nprandom



DPI = 100

INLET_CROSS_X = -200
INLET_CROSS_Y = 200
REACTOR_X = INLET_CROSS_X - 100
REACTOR_Y = -200
ACID_PUMP_X = REACTOR_X - 100
ACID_PUMP_Y = INLET_CROSS_Y - 100
TRAP_A_X = INLET_CROSS_X
TRAP_A_Y = 0
GAUGE_A_X = TRAP_A_X + 100
GAUGE_A_Y = TRAP_A_Y + 100
TRAP_B_X = TRAP_A_X + 200
TRAP_B_Y = TRAP_A_Y - 150
TRAP_C_X = TRAP_B_X + 200
TRAP_C_Y = TRAP_B_Y - 100
GAUGE_B_X = (TRAP_B_X + TRAP_C_X)//2
GAUGE_B_Y = TRAP_B_Y + 100
CRDS_X = TRAP_C_X + 200
CRDS_Y = TRAP_C_Y + 250
VACUUM_X = TRAP_C_X
VACUUM_Y = INLET_CROSS_Y + 150
TURBO_X = VACUUM_X - 90
TURBO_Y = VACUUM_Y - 180
SCROLL_X = VACUUM_X + 90
SCROLL_Y = VACUUM_Y - 180
GAUGE_C_X = VACUUM_X
GAUGE_C_Y = VACUUM_Y - 50
ACID_GAUGE_X = ACID_PUMP_X
ACID_GAUGE_Y = INLET_CROSS_Y + 100

from matplotlib import rcParams

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Helvetica'
rcParams['font.size'] = 10
rcParams['mathtext.fontset'] = 'custom'
rcParams['mathtext.rm'] = 'sans'
rcParams['mathtext.bf'] = 'sans:bold'
rcParams['mathtext.it'] = 'sans:italic'
rcParams['mathtext.cal'] = 'sans:italic'
rcParams['mathtext.default'] = 'rm'
rcParams['xtick.major.size'] = 4
rcParams['xtick.major.width'] = 1
rcParams['ytick.major.size'] = 4
rcParams['ytick.major.width'] = 1
rcParams['axes.grid'] = False
rcParams['axes.linewidth'] = 1
rcParams['grid.linewidth'] = .75
rcParams['grid.linestyle'] = '-'
rcParams['grid.alpha'] = .15
rcParams['savefig.dpi'] = DPI

def bg_img(
	figsize = (10, 8),
	):
	
	fig = figure(figsize = figsize)
	ax = axes((0, 0, 1, 1), frameon = False)

	tube_kwargs = dict(
		ls = '-',
		lw = 5,
		marker = 'None',
		color = 'k'
		)

	X, Y = zip(*[
		(ACID_PUMP_X, ACID_PUMP_Y),
		(ACID_GAUGE_X, ACID_GAUGE_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(ACID_GAUGE_X, INLET_CROSS_Y),
		(INLET_CROSS_X+100, INLET_CROSS_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(REACTOR_X, REACTOR_Y),
		(REACTOR_X, INLET_CROSS_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(TURBO_X, VACUUM_Y),
		(TURBO_X, TURBO_Y),
		(SCROLL_X, SCROLL_Y),
		(SCROLL_X, VACUUM_Y),
		(INLET_CROSS_X, VACUUM_Y),
		(TRAP_A_X, TRAP_A_Y),
		(TRAP_B_X, TRAP_A_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(GAUGE_A_X, TRAP_A_Y),
		(GAUGE_A_X, GAUGE_A_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(GAUGE_C_X, VACUUM_Y),
		(GAUGE_C_X, GAUGE_C_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(TRAP_B_X, VACUUM_Y),
		(TRAP_B_X, TRAP_B_Y),
		(TRAP_C_X, TRAP_B_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(GAUGE_B_X, TRAP_B_Y),
		(GAUGE_B_X, GAUGE_B_Y),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(TRAP_C_X, TRAP_C_Y),
		(TRAP_C_X, TRAP_B_Y+77),
		])
	plot(X, Y, **tube_kwargs)

	X, Y = zip(*[
		(TRAP_C_X, TRAP_B_Y+77),
		(TRAP_C_X, CRDS_Y),
		(CRDS_X, CRDS_Y),
		])
	tube_kwargs['lw'] = 2
	plot(X, Y, **tube_kwargs)

	ax.add_artist(
		Ellipse(
			xy = (CRDS_X, CRDS_Y),
			width = 95,
			height = 95,
			angle = 8.5,
			ec = 'k',
			fc = 'w',
			lw = 1,
			zorder = 100,
			ls = (0, (6,3)),
			)
		)

	crds_kwargs = dict(
		ls = '-',
		lw = 1.5,
		solid_capstyle = 'round',
		marker = 'None',
		color = (1,0,0),
		zorder = 200,
		)

	for k,a in enumerate(linspace(0,pi,13)[:-1]):
		l = 20 if k%2 else 30
		plot(
			[CRDS_X - l*cos(a), CRDS_X + (l if a else l*1.5)*cos(a)],
			[CRDS_Y - l*sin(a), CRDS_Y + l*sin(a)],
			**crds_kwargs
			)


# 	text(-500-10, 200, 'carrousel\ninlet', va = 'center', ha = 'right', size = 11)
# 	text(-400, 300+10, 'vacuum', va = 'bottom', ha = 'center', size = 11)
# 	text(-300+10, 200, 'manual\ninlet', va = 'center', ha = 'left', size = 11)

	axis([-figsize[0]*50, figsize[0]*50, -figsize[1]*50, figsize[1]*50])
	xticks([])
	yticks([])
	savefig('img/bg_img.png', dpi = DPI, facecolor = 'w')
	close(fig)

	
def valve(
	figsize = (1,1),
	radius = 0.2,
	lw = 5,
	color = 'k',
	alpha = 0.5,
	name = 'valve',
	):

	fig = figure(figsize = figsize)
	ax = axes((0, 0, 1, 1), frameon = False)

	l = array([-1, 1]) * radius / sqrt(2)
	plot( l, l, '-', color = color, solid_capstyle = 'butt', lw = lw)

	ax.add_artist(
		Ellipse(
			xy = (0, 0),
			width = 2*radius,
			height = 2*radius,
			ec = color,
			fc = 'w',
			lw = lw,
			)
		)

	axis([-figsize[0]/2, figsize[0]/2, -figsize[1]/2, figsize[1]/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}_closed.png', dpi = DPI, facecolor = 'None')
	close(fig)

	fig = figure(figsize = figsize)
	ax = axes((0, 0, 1, 1), frameon = False)

	ax.add_artist(
		Ellipse(
			xy = (0, 0),
			width = 2*radius,
			height = 2*radius,
			ec = color,
			fc = 'none',
			lw = lw,
			alpha = .25,
			)
		)

	axis([-figsize[0]/2, figsize[0]/2, -figsize[1]/2, figsize[1]/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}_open.png', dpi = DPI, facecolor = 'None')
	close(fig)


def trap(
	w = 1,
	h = 1,
	radius = 0.2,
	fc = (1,1,1,1),
	ec = 'k',
	lw = 2,
	name = 'trap',
	tube = '',
	tube_lw = 5,
	tube_color = 'k',
	):

	## clockwise from the top:
	circle = array([ [sin(a/360*2*pi), cos(a/360*2*pi)] for a in arange(361)])

	#draw box:
	xy = vstack((
			circle[:91]*radius + array([[w/2-radius, h/2-radius]]),
			array([
				[w/2, -h/2],
				[-w/2, -h/2],
				]),
			circle[270:]*radius + array([[-w/2+radius, h/2-radius]]),
			))
			

	fig = figure(figsize = (w+1,h+1))
	ax = axes((0, 0, 1, 1), frameon = False)
	ax.add_patch(
		Polygon(
			xy = xy,
			closed = True,
			ec = ec,
			fc = fc,
			lw = lw,
			)
		)
	if tube == 'L':
		plot([0,0,w/2], [h/2,0,0], '-', color = tube_color, lw = tube_lw, solid_capstyle = 'butt', solid_joinstyle = 'round')
	elif tube == 'I':
		plot([0,0,0], [h/2,0,h/2], '-', color = tube_color, lw = tube_lw, solid_capstyle = 'butt', solid_joinstyle = 'round')
	axis([-(w+1)/2, (w+1)/2, -(h+1)/2, (h+1)/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}.png', dpi = DPI, facecolor = 'None')
	close(fig)

def gauge(
	w = 1,
	h = .6,
	radius = 0.2,
	fc = (1,1,1,1),
	ec = 'k',
	lw = 2,
	name = 'gauge',
	):

	## clockwise from the top:
	circle = array([ [sin(a/360*2*pi), cos(a/360*2*pi)] for a in arange(361)])

	#draw box:
	xy = vstack((
			circle[:91]*radius + array([[w/2-radius, h/2-radius]]),
			circle[90:181]*radius + array([[w/2-radius, -h/2+radius]]),
			circle[180:271]*radius + array([[-w/2+radius, -h/2+radius]]),
			circle[270:]*radius + array([[-w/2+radius, h/2-radius]]),
			))
			

	fig = figure(figsize = (w+1,h+1))
	ax = axes((0, 0, 1, 1), frameon = False)
	ax.add_patch(
		Polygon(
			xy = xy,
			closed = True,
			ec = ec,
			fc = fc,
			lw = lw,
			)
		)
	axis([-(w+1)/2, (w+1)/2, -(h+1)/2, (h+1)/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}.png', dpi = DPI, facecolor = 'None')
	close(fig)

def disk(
	w = 1,
	h = 1,
	radius = 0.2,
	fc = (1,1,1,1),
	ec = 'k',
	lw = 2,
	name = 'disk',
	):

	fig = figure(figsize = (w+1,h+1))
	ax = axes((0, 0, 1, 1), frameon = False)
	ax.add_patch(
		Ellipse(
			xy = (0,0),
			width = w, height = h,
			ec = ec,
			fc = fc,
			lw = lw,
			)
		)
	axis([-(w+1)/2, (w+1)/2, -(h+1)/2, (h+1)/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}.png', dpi = DPI, facecolor = 'None')
	close(fig)

def thermostat(
	w = 1,
	h = .5,
	radius = 0.2,
	fc = (1,1,1,1),
	ec = 'k',
	lw = 2,
	name = 'thermostat',
	):

	## clockwise from the top:
	circle = array([ [sin(a/360*2*pi), cos(a/360*2*pi)] for a in arange(361)])

	#draw box:
	xy = vstack((
			array([
				[-w/2, h/2],
				[w/2, h/2],
				]),
			circle[90:181]*radius + array([[w/2-radius, -h/2+radius]]),
			circle[180:271]*radius + array([[-w/2+radius, -h/2+radius]]),
			))

	fig = figure(figsize = (w+1,h+1))
	ax = axes((0, 0, 1, 1), frameon = False)
	ax.add_patch(
		Polygon(
			xy = xy,
			closed = True,
			ec = ec,
			fc = fc,
			lw = lw,
			)
		)
	axis([-(w+1)/2, (w+1)/2, -(h+1)/2, (h+1)/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}.png', dpi = DPI, facecolor = 'None')
	close(fig)

def button(
	w = .3,
	h = .3,
	fc = (1,1,1,1),
	ec = 'k',
	lw = 2,
	name = 'button',
	symbol = '',
	symbol_size = .2,
	symbol_dx = 0.,
	symbol_dy = 0.,
	symbol_lw = 2,
	symbol_color = 'k',
	):

	#draw box:
	xy = array([
		[w/2, h/2],
		[w/2, -h/2],
		[-w/2, -h/2],
		[-w/2, h/2],
		])			

	fig = figure(figsize = (w+1,h+1))
	ax = axes((0, 0, 1, 1), frameon = False)
	ax.add_patch(
		Polygon(
			xy = xy,
			closed = True,
			ec = ec,
			fc = fc,
			lw = lw,
			)
		)
	if symbol == 'snowflake':
		text(0 + symbol_dx, 0 + symbol_dy, '❄︎'[:-1], family = 'Menlo', size = symbol_size, ha = 'center', va = 'center')
	elif symbol == 'hot':
		text(0 + symbol_dx, 0 + symbol_dy, '≈', family = 'Menlo', size = symbol_size, ha = 'center', va = 'center', rotation = 90)
	elif symbol in ['ufwd', 'fwd', 'ubwd', 'bwd']:
		l = symbol_size/300
		ax.add_patch(
			Polygon(
				xy = [(l*cos(a)*(1 if symbol in ['fwd', 'ufwd'] else -1) + symbol_dx, l*sin(a) + symbol_dy) for a in [0, 2*pi/3, -2*pi/3]],
				closed = True,
				ec = symbol_color,
				fc = symbol_color,
				lw = symbol_lw,
				)
			)
		if symbol in ['bwd', 'fwd']:
			plot([(l*1.2+symbol_dx) if symbol == 'fwd' else (-l*1.2+symbol_dx)]*2, [-l+symbol_dy, l-symbol_dy], '-', color = symbol_color, lw = symbol_lw)
	else:
		text(0 + symbol_dx, 0 + symbol_dy, symbol, family = 'Helvetica', size = symbol_size, ha = 'center', va = 'center', color = symbol_color, weight = 'bold')

	axis([-(w+1)/2, (w+1)/2, -(h+1)/2, (h+1)/2])
	xticks([])
	yticks([])
	savefig(f'img/{name}.png', dpi = DPI, facecolor = 'None')
	close(fig)

def acidbath(
	radius = .5,
	lw = 3,
	hs_color = 'w',
	acid_color = (.75,1,.75,1),
	bubble_fc = (1,1,1,2/3),
	n_bubbles = 16,
	min_bubble_radius = .05,
	max_bubble_radius = .15,
	seed = 16,
	bubble_dx = +0.,
	bubble_dy = -0.,
	bubble_lw = 1,
	):

	## clockwise from the top:
	circle = array([ [sin(a/360*2*pi), cos(a/360*2*pi)] for a in arange(361)])
	
	#draw box:
	xy1 = vstack((
			array([[1, .5]]),
			circle[90:271] - array([[0, .5]]),
			array([[-1, .5]]),
			))*radius

	xy2 = vstack((
			circle[270:] + array([[0, .5]]),
			circle[:91] + array([[0, .5]]),
			))*radius

	fig = figure(figsize = (2*radius + .2, 3*radius + .2))
	ax = axes((0, 0, 1, 1), frameon = False)
	plot([-radius, radius], [radius/2, radius/2], 'k-', lw = bubble_lw, solid_capstyle = 'butt')
	ax.add_patch(
		Polygon(
			xy = xy2,
			closed = False,
			ec = 'k',
			fc = 'w',
			lw = lw,
			)
		)
	ax.add_patch(
		Polygon(
			xy = xy1,
			closed = False,
			ec = 'k',
			fc = acid_color,
			lw = lw,
			)
		)
	
	rng = nprandom.default_rng(seed)
	for k in range(n_bubbles):
		r = rng.uniform(min_bubble_radius*radius, max_bubble_radius*radius)
		x = rng.uniform(-radius*0.9, radius*0.9)+bubble_dx
		y = rng.uniform(-radius*0.9, radius*0.9)+bubble_dy

		ax.add_artist(
			Ellipse(
				xy = (x,y-x/10),
				width = 2*r,
				height = 2*r,
				ec = 'k',
				fc = bubble_fc,
				lw = bubble_lw,
				zorder = 100,
				)
			)
		
	axis([-(radius+.1), (radius+.1), -(1.5*radius+.1), (1.5*radius+.1)])
	xticks([])
	yticks([])
	savefig(f'img/acid_{seed:03.0f}.png', dpi = DPI, facecolor = 'None')
	close(fig)
	
def command(
	name = 'command',
	w = 0.75,
	h = 0.15,
	fc = (1,1,1,1),
	ec = (0,0,0,1),
	lw = 2,
	label = '',
	size = 14,
	tc = (0,0,0,1),
	weight = 'bold',
	dx = 0,
	dy = 0,
	):
	fig = figure(figsize = (w+1, h+1))
	ax = axes((0, 0, 1, 1), frameon = False)

	x = [-w, w, w, -w, -w]
	y = [h, h, -h, -h, h]
	xy = array([x, y]).T
	ax.add_artist(
		Polygon(xy,
			ec = 'none',
			fc = fc,
			)
		)
	plot(x, y, '-', color = ec, lw = lw, solid_capstyle = 'round', solid_joinstyle = 'round')
	text(dx, dy, label, va = 'center', ha = 'center', size = size, color = tc, weight = weight)
	axis([-(w+1)/2, (w+1)/2, -(h+1)/2, (h+1)/2])
	xticks([])
	yticks([])
	savefig(f'img/command_{name}.png', dpi = DPI, facecolor = 'None')
	close(fig)


if __name__ == '__main__':

	for symbol, w, h, symbol_size, symbol_dx, symbol_dy, fc, ec, name, symbol_color in [
		('STOP, FOR REAL', 6.8, 1, 36, 0., -0.05, (1,0,0,1), (.75,0,0,1), 'stop_for_real', 'w'),
		('NO, NEVER MIND', 6.8, 1, 36, 0., -0.05, (.75,.75,.75,1), (.5,.5,.5,1), 'no_never_mind', (.5,.5,.5)),
		]:
		button(w = w, h = h, fc = fc, ec = ec, symbol = symbol, symbol_dx = symbol_dx, symbol_dy = symbol_dy, symbol_size = symbol_size, name = f'command_{name}', symbol_color = symbol_color)

	for name, fc, ec, label, tc, dx, dy in [
		('transfer', (.75,.75,.75,1), (.5,.5,.5,1), 'TRANSFER', (1,1,1,1), 0, -.025),
		('standby', (.5,.5,.5,1), (.25,.25,.25,1), 'STANDBY', (1,1,1,1), 0, -.025),
		('carb', (.9,.6,1,1), (.1,0,.2,1), 'RUN CARB', None, 0, -.025),
		('CO2', (.8,.9,1,1), (0,0,.5,1), 'RUN CO2', None, 0, -.025),
		('stop', (2/3,0,0,1), (.25,0,0,1), 'STOP', (1,1,1,1), 0, -.025),
		]:
		command(
			name = name,
			fc = fc,
			ec = ec,
			label = label,
			tc = ec if tc is None else tc,
			dx = dx,
			dy = dy,
			)

# 	for k in range(30):
# 		acidbath(seed = k)
	
	acidbath(seed = 130, bubble_dy  = -0.11)
	
	bg_img()
	
	for symbol, symbol_size, symbol_dx, symbol_dy, fc, color, symbol_color in [
		('hot', 24, 0.01, 0.016, (1,.75,0,1), 'orange', 'k'),
		('hot', 24, 0.01, 0.016, (1,1,1,1), 'white', 'k'),
		('snowflake', 24, 0, -0.021, (0,1,1,1), 'cyan', 'k'),
		('snowflake', 24, 0, -0.021, (1,1,1,1), 'white', 'k'),
		('snowflake', 16, 0, -0.018, (.9,.75,1,1), 'magenta', 'k'),
		('snowflake', 16, 0, -0.018, (1,1,1,1), 'white', 'k'),
		('ubwd', 12, 0.01, 0., (1,1,1,1), 'white', (2/3,2/3,2/3,1)),
		('ufwd', 12, 0, 0., (1,1,1,1), 'white', (2/3,2/3,2/3,1)),
		('fwd', 20, -0.01, 0., (1,1,1,1), 'white', 'k'),
		('bwd', 20, 0.02, 0., (1,1,1,1), 'white', 'k'),
		]:
		button(fc = fc, symbol = symbol, symbol_dx = symbol_dx, symbol_dy = symbol_dy, symbol_size = symbol_size, name = f'button_{symbol}_{symbol_size}_{color}', symbol_color = symbol_color)

	for fc, name in [
			('w', 'white'),
			((1,.75,0,1), 'orange'),
			((0,1,1,1), 'cyan'),
			((.3,.9,1,1), 'lightblue'),
			((.9,.75,1,1), 'magenta'),
			((1,.9,.4,1), 'yellow'),
			((.25,1,0,1), 'green'),
			((1,0,0,1), 'red'),
			]:
		thermostat(fc = fc, name = f'thermostat_{name}')
		gauge(fc = fc, name = f'gauge_{name}')
		disk(fc = fc, name = f'pump_{name}')
		for tube in 'LI':
			trap(tube = tube, fc = fc, name = f'trap_{tube}_{name}')

	valve()

	exit()

# def needle_display(
# 	x = 0,
# 	y = 0,
# 	r1 = 44,
# 	r2 = 100,
# 	orientation = 90,
# 	span = 100,
# 	ec = (0,0,0),
# 	lw = 1,
# 	):
# 	ax = gca()
# 
# 	for t in [orientation - span/2, orientation + span/2]:
# 		plot(
# 			[x + r1 * cos(t*pi/180), x + r2 * cos(t*pi/180)],
# 			[y + r1 * sin(t*pi/180), y + r2 * sin(t*pi/180)],
# 			'-', color = ec, lw = lw,
# 			)
# 	
# 	for r in [r1, r2]:
# 		ax.add_artist(
# 			Arc((x, y),
# 				width = 2*r,
# 				height = 2*r,
# 				theta1 = orientation - span/2,
# 				theta2 = orientation + span/2,
# 				ec = ec,
# 				fc = 'none',
# 				lw = lw,
# 				)
# 			)
# 	
# 	
# 
# ### CANVAS
# fig = figure(figsize = (12, 8))
# ax = axes((0, 0, 1, 1), frameon = False)
# # text(300, -60, '[ ]', color = (0,0,1), **kwargs)
# 
# # needle_display(0, 100)
# # needle_display(280, 100)
# 
# tube_kwargs = dict(
# 	ls = '-',
# 	lw = 5,
# 	marker = 'None',
# 	color = 'k'
# 	)
# X, Y = zip(*[
# 	(-500, 200),
# 	(-300, 200),
# 	])
# plot(X, Y, **tube_kwargs)
# X, Y = zip(*[
# 	(-400, 300),
# 	(-400, -100),
# 	(-200, -100),
# 	(-200, -300),
# 	])
# plot(X, Y, **tube_kwargs)
# 
# X, Y = zip(*[
# 	(-300, -100),
# 	(-300, -60),
# 	])
# plot(X, Y, **tube_kwargs)
# 
# # needle_display(-300, -80, r1 = 28, r2 = 62)
# 
# text(-500-10, 200, 'carrousel\ninlet', va = 'center', ha = 'right', size = 11)
# text(-400, 300+10, 'vacuum', va = 'bottom', ha = 'center', size = 11)
# text(-300+10, 200, 'manual\ninlet', va = 'center', ha = 'left', size = 11)
# 
# axis([-600, 600, -400, 400])
# xticks([])
# yticks([])
# savefig('img/bg_img.png', dpi = DPI, facecolor = 'w')
# close(fig)
# 
# 
# ### VALVE_CLOSED
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# kwargs = dict(ls = '-', lw = VALVE_THICKNESS)
# 
# l = array([-1, 1]) * VALVE_RADIUS / sqrt(2)
# plot( l, l, 'k-', solid_capstyle = 'butt', **kwargs )
# 
# ax.add_artist(
# 	Ellipse(
# 		xy = (0, 0),
# 		width = 2*VALVE_RADIUS,
# 		height = 2*VALVE_RADIUS,
# 		ec = 'k',
# 		fc = 'w',
# 		**kwargs
# 		)
# 	)
# 
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/valve_closed.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# 
# ### VALVE_OPEN
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# ax.add_artist(
# 	Ellipse(
# 		xy = (0, 0),
# 		width = 2*VALVE_RADIUS,
# 		height = 2*VALVE_RADIUS,
# 		ec = 'k',
# 		fc = 'none',
# 		alpha = .25,
# 		**kwargs
# 		)
# 	)
# 
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/valve_open.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# 
# ### LOGGER STOP
# fig = figure(figsize = (.4, .4))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# plot(0, 0, 'o', mfc = (.8,0,0), ms = 26, mew = 0)
# plot([-0.05]*2, [-0.05, 0.05], 'w-', lw = 4)
# plot([0.05]*2, [-0.05, 0.05], 'w-', lw = 4)
# 
# axis([-0.2, 0.2, -0.2, 0.2])
# xticks([])
# yticks([])
# savefig('img/logger_stop.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# ### LOGGER start
# fig = figure(figsize = (.4, .4))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# plot(0, 0, 'o', mfc = 'None', mec = (.75,.75,.75), ms = 25, mew = 1)
# plot(0.004, -0.002, 's', mew = 0, ms = 12, mfc = (.8,0,0))
# 
# axis([-0.2, 0.2, -0.2, 0.2])
# xticks([])
# yticks([])
# savefig('img/logger_start.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# 
# ### NEEDLE
# fig = figure(figsize = (.5, 2))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# w, h, d = .015, .3, .6
# x = [-w, 0, w, -w]
# y = [d-h, d, d-h, d-h]
# xy = array([x, y]).T
# plot(x, y, 'k-', lw = 1, solid_capstyle = 'round', solid_joinstyle = 'round')
# ax.add_artist(
# 	Polygon(xy,
# 		ec = 'none',
# 		fc = 'r',
# 		zorder = 100,
# 		)
# 	)
# 
# axis([-0.25, 0.25, -1, 1])
# xticks([])
# yticks([])
# savefig('img/needle.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# ### NEEDLE
# fig = figure(figsize = (.5, 2))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# plot([0,0], [.3,.6], '-', color = (1,0,0,.75), lw = 2, solid_capstyle = 'butt')
# 
# axis([-0.25, 0.25, -1, 1])
# xticks([])
# yticks([])
# savefig('img/needle_line.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# 
# ### BLINK DIALOG
# for diag, file in [('START', 'button_start'), ('STOP', 'button_stop')]:
# 	fig = figure(figsize = (1, .5))
# 	ax = axes((0, 0, 1, 1), frameon = False)
# 
# 	w, h = .8/2, .3/2
# 	x = [-w, w, w, -w, -w]
# 	y = [h, h, -h, -h, h]
# 	xy = array([x, y]).T
# 	ax.add_artist(
# 		Polygon(xy,
# 			ec = 'none',
# 			fc = (1, 0, 0, 1) if diag == 'STOP' else (0, .5, 0, 1),
# 	# 		zorder = 100,
# 			)
# 		)
# 	plot(x, y, '-', color = (.75, 0, 0, 1) if diag == 'STOP' else (0, .25, 0, 1), lw = 1, solid_capstyle = 'round', solid_joinstyle = 'round')
# 	text(0.5, 0.45, diag, transform = fig.transFigure, va = 'center', ha = 'center', size = 14, color = 'w', weight = 'bold', zorder  =200)
# 	axis([-0.5, 0.5, -.25, .25])
# 	xticks([])
# 	yticks([])
# 	savefig(f'img/{file}.png', dpi = DPI, facecolor = 'None')
# 	close(fig)
# 
# ### FWD DIALOG
# for diag, file in [('FWD', 'button_fwd'), ('BWD', 'button_bwd')]:
# 	fig = figure(figsize = (1, .5))
# 	ax = axes((0, 0, 1, 1), frameon = False)
# 
# 	w, h = .8/2, .3/2
# 	x = [-w, w, w, -w, -w]
# 	y = [h, h, -h, -h, h]
# 	xy = array([x, y]).T
# 	ax.add_artist(
# 		Polygon(xy,
# 			ec = 'none',
# 			fc = (1, 0, 0, 1) if diag == 'BWD' else (0, .5, 0, 1),
# 	# 		zorder = 100,
# 			)
# 		)
# 	plot(x, y, '-', color = (.75, 0, 0, 1) if diag == 'BWD' else (0, .25, 0, 1), lw = 1, solid_capstyle = 'round', solid_joinstyle = 'round')
# 	text(0.5, 0.45, diag, transform = fig.transFigure, va = 'center', ha = 'center', size = 14, color = 'w', weight = 'bold', zorder  =200)
# 	axis([-0.5, 0.5, -.25, .25])
# 	xticks([])
# 	yticks([])
# 	savefig(f'img/{file}.png', dpi = DPI, facecolor = 'None')
# 	close(fig)
# 
# 
# ### CANCEL DIALOG
# for diag, file in [('ABORT', 'button_abort'), ('UNDO', 'button_undo')]:
# 	fig = figure(figsize = (3, 1))
# 	ax = axes((0, 0, 1, 1), frameon = False)
# 
# 	w, h = 2.8/2, .8/2
# 	x = [-w, w, w, -w, -w]
# 	y = [h, h, -h, -h, h]
# 	xy = array([x, y]).T
# 	ax.add_artist(
# 		Polygon(xy,
# 			ec = 'none',
# 			fc = (1, 0, 0, 1) if diag == 'ABORT' else (.75, .75, .75, 1),
# 	# 		zorder = 100,
# 			)
# 		)
# 	plot(x, y, '-', color = (.75, 0, 0, 1) if diag == 'ABORT' else (.5, .5, .5, 1), lw = 2, solid_capstyle = 'round', solid_joinstyle = 'round')
# 	text(0.5, 0.45, diag, transform = fig.transFigure, va = 'center', ha = 'center', size = 32, color = 'w', weight = 'bold', zorder  =200)
# 	axis([-1.5, 1.5, -.5, .5])
# 	xticks([])
# 	yticks([])
# 	savefig(f'img/{file}.png', dpi = DPI, facecolor = 'None')
# 	close(fig)
# 
# ### HOT_BOX
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# ax.add_artist(
# 	FancyBboxPatch(
# 		xy = (-.3, -.3),
# 		width = .6,
# 		height = .6,
# 		boxstyle = BoxStyle("Round", pad=0.05),
# 		ec = 'k',
# 		fc = (1,.6,0,1),
# 		ls = '-',
# 		lw = 2,
# 		)
# 	)
# 
# plot([0,0,.3], [.3,0,0], **tube_kwargs)
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/hot_box.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# ### COLD_BOX
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# ax.add_artist(
# 	FancyBboxPatch(
# 		xy = (-.3, -.3),
# 		width = .6,
# 		height = .6,
# 		boxstyle = BoxStyle("Round", pad=0.05),
# 		ec = 'k',
# 		fc = (.25,1,1,1),
# 		ls = '-',
# 		lw = 2,
# 		)
# 	)
# 
# plot([0,0,.3], [.3,0,0], **tube_kwargs)
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/cold_box.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# ### DEFAULT_BOX
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# ax.add_artist(
# 	FancyBboxPatch(
# 		xy = (-.3, -.3),
# 		width = .6,
# 		height = .6,
# 		boxstyle = BoxStyle("Round", pad=0.05),
# 		ec = 'k',
# 		fc = (1,.5,0,0),
# 		ls = '-',
# 		lw = 2,
# 		)
# 	)
# 
# plot([0,0,.3], [.3,0,0], **tube_kwargs)
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/tepid_box.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# 
# ### COOL_BOX
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# ax.add_artist(
# 	FancyBboxPatch(
# 		xy = (-.3, -.3),
# 		width = .6,
# 		height = .6,
# 		boxstyle = BoxStyle("Round", pad=0.05),
# 		ec = 'k',
# 		fc = (.6,.9,1),
# # 		fc = (.8,.7,1),
# # 		fc = (.8,.95,.8),
# 		ls = '-',
# 		lw = 2,
# 		)
# 	)
# 
# plot([0,0,.3], [.3,0,0], **tube_kwargs)
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/cool_box.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# ### COLD_BOX
# fig = figure(figsize = (1,1))
# ax = axes((0, 0, 1, 1), frameon = False)
# 
# ax.add_artist(
# 	FancyBboxPatch(
# 		xy = (-.3, -.3),
# 		width = .6,
# 		height = .6,
# 		boxstyle = BoxStyle("Round", pad=0.05),
# 		ec = 'k',
# 		fc = (0,1,1),
# 		ls = '-',
# 		lw = 2,
# 		)
# 	)
# plot([0,0,.3], [.3,0,0], **tube_kwargs)
# axis([-0.5, 0.5, -0.5, 0.5])
# xticks([])
# yticks([])
# savefig('img/cold_box.png', dpi = DPI, facecolor = 'None')
# close(fig)
# 
# for color, name in [
# 	((1,1,1), 'default'),
# 	((.25,1,0), 'green'),
# 	((1,1,.67), 'yellow'),
# 	]:
# 	h, w = .75, .75
# 	Ncurve = 180
# 	fig = figure(figsize = (4,1))
# 	ax = axes((0, 0, 1, 1), frameon = False)
# 	xy = [
# 		(-(w-h)/2, h/2),
# 		((w-h)/2, h/2),
# 		]
# 	for k in range(Ncurve-1):
# 		xy += [((w-h)/2 + h/2*sin((k+1)/Ncurve*pi), h/2*cos((k+1)/Ncurve*pi))]
# 	xy += [	
# 		((w-h)/2, -h/2),
# 		(-(w-h)/2, -h/2),
# 		]
# 	for k in range(Ncurve-1):
# 		xy += [(-(w-h)/2 - h/2*sin((k+1)/Ncurve*pi), -h/2*cos((k+1)/Ncurve*pi))]
# 	ax.add_patch(
# 		Polygon(
# 			xy = xy,
# 			closed = True,
# 			ec = 'k',
# 			fc = color,
# 			lw = 2,
# 			)
# 		)
# 	axis([-2, 2, -0.5, 0.5])
# 	xticks([])
# 	yticks([])
# 	savefig(f'img/oval_{name}.png', dpi = DPI, facecolor = 'None')
# 	close(fig)
