import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from moviepy.video.io.bindings import mplfig_to_npimage
from moviepy.editor import VideoClip
import moviepy.editor as mpy

duration = 4

font = {'family' : 'serif',
        'weight' : 'normal',
        'size'   : 10,
        }

def custom_legend(legend):
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    
    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize(11)

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
        

def read_data(i):
    m = np.load('beta_0.05_u_400/dyn_npys/m_%d.npy'%i)
    m.shape = (-1,3)
    mx = m[:,0]
    m2 = np.load('beta_0.1_u_500/dyn_npys/m_%d.npy'%i)
    m2.shape = (-1,3)
    mx2 = m2[:,0]
    return mx, mx2

fig = plt.figure(figsize=(6, 3.2))
    
gs = gridspec.GridSpec(2, 1,height_ratios=[1,1])

fig_mpl, ax1 = plt.subplots(1,figsize=(8,2.6), facecolor='white')
xs = np.linspace(0.5,3999.5,4000) # the x vector
m1,m2 = read_data(0)

ax1 = plt.subplot(gs[0])
p1,= ax1.plot(xs,m1*1e4,'-', linewidth=0.8, color='chocolate', label=r'$\beta=0.05, u=400$ m/s')   

#
ax1.set_ylabel('$m_x$ $[10^{-4}]$')
ax1.set_ylim(-2,2)
plt.yticks([-2, 0, 2])
plt.xticks([])
l1 = plt.legend(loc='upper right', shadow=True, frameon=False,labelspacing=0, handletextpad=0.3)
custom_legend(l1)

ax2 = plt.subplot(gs[1])
p2,= ax2.plot(xs,m2*1e3,'-', linewidth=0.8, color='steelblue', label=r'$\beta=0.1, u=500$ m/s')
ax2.set_xlabel('z/a')
ax2.set_ylabel('$m_x$ $[10^{-3}]$')
ax2.set_ylim(-1,1)
plt.yticks([-1, 0, 1])

l2 = plt.legend(loc='upper right', shadow=True, frameon=False,labelspacing=0, handletextpad=0.3)
custom_legend(l2)
plt.tight_layout()
plt.subplots_adjust(left=0.105, bottom=0.18, right=0.965, top=0.9, hspace=0.1)
 
# ANIMATE WITH MOVIEPY (UPDATE THE CURVE FOR EACH t). MAKE A GIF.

def make_frame_mpl(t):
    #print(int(t*10))
    m1,m2 = read_data(int(t*10))
    p1.set_ydata(m1*1e4)
    p2.set_ydata(m2*1e3)
    ax1.set_title('t=%0.2f ns'%(t*0.2))
    return mplfig_to_npimage(fig_mpl) # RGB image of the figure
 
animation = mpy.VideoClip(make_frame_mpl, duration=duration)
animation.write_gif("II.gif", fps=10)
