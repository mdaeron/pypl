#! /usr/bin/env python3

from matplotlib.patches import *
from pylab import *

DPI = 100
VALVE_RADIUS = 0.4
VALVE_THICKNESS = 10	
	

def needle_display(
	x = 0,
	y = 0,
	r1 = 44,
	r2 = 100,
	orientation = 90,
	span = 100,
	ec = (0,0,0),
	lw = 1,
	):
	ax = gca()

	for t in [orientation - span/2, orientation + span/2]:
		plot(
			[x + r1 * cos(t*pi/180), x + r2 * cos(t*pi/180)],
			[y + r1 * sin(t*pi/180), y + r2 * sin(t*pi/180)],
			'-', color = ec, lw = lw,
			)
	
	for r in [r1, r2]:
		ax.add_artist(
			Arc((x, y),
				width = 2*r,
				height = 2*r,
				theta1 = orientation - span/2,
				theta2 = orientation + span/2,
				ec = ec,
				fc = 'none',
				lw = lw,
				)
			)
	
	

### CANVAS
fig = figure(figsize = (10, 7))
ax = axes((0, 0, 1, 1), frameon = False)
kwargs = dict(size = 120, ha = 'center', va = 'center')
text(-200, -160, '[ ]', color = (1,0,0), **kwargs)
text(-000, -160, '[ ]', color = (0,1,0), **kwargs)
text(200, -160, '[ ]', color = (1,.5,0), **kwargs)
# text(300, -60, '[ ]', color = (0,0,1), **kwargs)

needle_display(-280, 100)
needle_display(0, 100)
needle_display(280, 100)

axis([-500, 500, -350, 350])
xticks([])
yticks([])
savefig('bg_img.png', dpi = DPI, facecolor = 'w')
close(fig)


### VALVE_CLOSED
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)
kwargs = dict(ls = '-', lw = VALVE_THICKNESS)

l = array([-1, 1]) * VALVE_RADIUS / sqrt(2)
plot( l, l, 'k-', solid_capstyle = 'butt', **kwargs )

ax.add_artist(
	Ellipse(
		xy = (0, 0),
		width = 2*VALVE_RADIUS,
		height = 2*VALVE_RADIUS,
		ec = 'k',
		fc = 'none',
		**kwargs
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('valve_closed.png', dpi = DPI, facecolor = 'None')
close(fig)


### VALVE_OPEN
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)

ax.add_artist(
	Ellipse(
		xy = (0, 0),
		width = 2*VALVE_RADIUS,
		height = 2*VALVE_RADIUS,
		ec = 'k',
		fc = 'none',
		alpha = .25,
		**kwargs
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('valve_open.png', dpi = DPI, facecolor = 'None')
close(fig)


### LOGGER STOP
fig = figure(figsize = (.4, .4))
ax = axes((0, 0, 1, 1), frameon = False)

plot(0, 0, 'o', mfc = (.8,0,0), ms = 26, mew = 0)
plot([-0.05]*2, [-0.05, 0.05], 'w-', lw = 4)
plot([0.05]*2, [-0.05, 0.05], 'w-', lw = 4)

axis([-0.2, 0.2, -0.2, 0.2])
xticks([])
yticks([])
savefig('logger_stop.png', dpi = DPI, facecolor = 'None')
close(fig)

### LOGGER start
fig = figure(figsize = (.4, .4))
ax = axes((0, 0, 1, 1), frameon = False)

plot(0, 0, 'o', mfc = 'None', mec = (.75,.75,.75), ms = 25, mew = 1)
plot(0.004, -0.002, 's', mew = 0, ms = 12, mfc = (.8,0,0))

axis([-0.2, 0.2, -0.2, 0.2])
xticks([])
yticks([])
savefig('logger_start.png', dpi = DPI, facecolor = 'None')
close(fig)


### NEEDLE
fig = figure(figsize = (.5, 2))
ax = axes((0, 0, 1, 1), frameon = False)

w, h = .025, .5
x = [-w, 0, w, -w]
y = [.95-h, .95, .95-h, .95-h]
xy = array([x, y]).T
plot(x, y, 'k-', lw = 1, solid_capstyle = 'round', solid_joinstyle = 'round')
ax.add_artist(
	Polygon(xy,
		ec = 'none',
		fc = 'r',
		zorder = 100,
		)
	)

axis([-0.25, 0.25, -1, 1])
xticks([])
yticks([])
savefig('needle.png', dpi = DPI, facecolor = 'None')
close(fig)


### BLINK DIALOG
for diag, file in [('START', 'button_start'), ('STOP', 'button_stop')]:
	fig = figure(figsize = (1, .5))
	ax = axes((0, 0, 1, 1), frameon = False)

	w, h = .8/2, .3/2
	x = [-w, w, w, -w, -w]
	y = [h, h, -h, -h, h]
	xy = array([x, y]).T
	ax.add_artist(
		Polygon(xy,
			ec = 'none',
			fc = (1, 0, 0, 1) if diag == 'STOP' else (0, .5, 0, 1),
	# 		zorder = 100,
			)
		)
	plot(x, y, '-', color = (.75, 0, 0, 1) if diag == 'STOP' else (0, .25, 0, 1), lw = 1, solid_capstyle = 'round', solid_joinstyle = 'round')
	text(0.5, 0.45, diag, transform = fig.transFigure, va = 'center', ha = 'center', size = 14, color = 'w', weight = 'bold', zorder  =200)
	axis([-0.5, 0.5, -.25, .25])
	xticks([])
	yticks([])
	savefig(f'{file}.png', dpi = DPI, facecolor = 'None')
	close(fig)

### FWD DIALOG
for diag, file in [('FWD', 'button_fwd'), ('BWD', 'button_bwd')]:
	fig = figure(figsize = (1, .5))
	ax = axes((0, 0, 1, 1), frameon = False)

	w, h = .8/2, .3/2
	x = [-w, w, w, -w, -w]
	y = [h, h, -h, -h, h]
	xy = array([x, y]).T
	ax.add_artist(
		Polygon(xy,
			ec = 'none',
			fc = (1, 0, 0, 1) if diag == 'BWD' else (0, .5, 0, 1),
	# 		zorder = 100,
			)
		)
	plot(x, y, '-', color = (.75, 0, 0, 1) if diag == 'BWD' else (0, .25, 0, 1), lw = 1, solid_capstyle = 'round', solid_joinstyle = 'round')
	text(0.5, 0.45, diag, transform = fig.transFigure, va = 'center', ha = 'center', size = 14, color = 'w', weight = 'bold', zorder  =200)
	axis([-0.5, 0.5, -.25, .25])
	xticks([])
	yticks([])
	savefig(f'{file}.png', dpi = DPI, facecolor = 'None')
	close(fig)


### CANCEL DIALOG
for diag, file in [('ABORT', 'button_abort'), ('UNDO', 'button_undo')]:
	fig = figure(figsize = (3, 1))
	ax = axes((0, 0, 1, 1), frameon = False)

	w, h = 2.8/2, .8/2
	x = [-w, w, w, -w, -w]
	y = [h, h, -h, -h, h]
	xy = array([x, y]).T
	ax.add_artist(
		Polygon(xy,
			ec = 'none',
			fc = (1, 0, 0, 1) if diag == 'ABORT' else (.75, .75, .75, 1),
	# 		zorder = 100,
			)
		)
	plot(x, y, '-', color = (.75, 0, 0, 1) if diag == 'ABORT' else (.5, .5, .5, 1), lw = 2, solid_capstyle = 'round', solid_joinstyle = 'round')
	text(0.5, 0.45, diag, transform = fig.transFigure, va = 'center', ha = 'center', size = 32, color = 'w', weight = 'bold', zorder  =200)
	axis([-1.5, 1.5, -.5, .5])
	xticks([])
	yticks([])
	savefig(f'{file}.png', dpi = DPI, facecolor = 'None')
	close(fig)

### HOT_BOX
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)

ax.add_artist(
	FancyBboxPatch(
		xy = (-.3, -.3),
		width = .6,
		height = .6,
		boxstyle = BoxStyle("Round", pad=0.1),
		ec = 'k',
		fc = (1,.6,0,1),
		ls = '-',
		lw = 4,
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('hot_box.png', dpi = DPI, facecolor = 'None')
close(fig)

### COLD_BOX
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)

ax.add_artist(
	FancyBboxPatch(
		xy = (-.3, -.3),
		width = .6,
		height = .6,
		boxstyle = BoxStyle("Round", pad=0.1),
		ec = 'k',
		fc = (.25,1,1,1),
		ls = '-',
		lw = 4,
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('cold_box.png', dpi = DPI, facecolor = 'None')
close(fig)

### DEFAULT_BOX
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)

ax.add_artist(
	FancyBboxPatch(
		xy = (-.3, -.3),
		width = .6,
		height = .6,
		boxstyle = BoxStyle("Round", pad=0.1),
		ec = 'k',
		fc = (1,.5,0,0),
		ls = '-',
		lw = 4,
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('tepid_box.png', dpi = DPI, facecolor = 'None')
close(fig)


### COOL_BOX
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)

ax.add_artist(
	FancyBboxPatch(
		xy = (-.3, -.3),
		width = .6,
		height = .6,
		boxstyle = BoxStyle("Round", pad=0.1),
		ec = 'k',
		fc = (.6,.9,1),
# 		fc = (.8,.7,1),
# 		fc = (.8,.95,.8),
		ls = '-',
		lw = 4,
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('cool_box.png', dpi = DPI, facecolor = 'None')
close(fig)

### COLD_BOX
fig = figure(figsize = (1,1))
ax = axes((0, 0, 1, 1), frameon = False)

ax.add_artist(
	FancyBboxPatch(
		xy = (-.3, -.3),
		width = .6,
		height = .6,
		boxstyle = BoxStyle("Round", pad=0.1),
		ec = 'k',
		fc = (0,1,1),
		ls = '-',
		lw = 4,
		)
	)

axis([-0.5, 0.5, -0.5, 0.5])
xticks([])
yticks([])
savefig('cold_box.png', dpi = DPI, facecolor = 'None')
close(fig)
