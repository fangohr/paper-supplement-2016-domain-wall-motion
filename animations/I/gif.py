import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from moviepy.video.io.bindings import mplfig_to_npimage
from moviepy.editor import VideoClip
import moviepy.editor as mpy

duration = 27
#duration = 0.5

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


ts1 = []
ts2 = []
u1 = []
u2 = []
def varying_u(t):
    t=t%2.0
    if t<=1.0 and t!=0.0:
        return 0
    else:
        return 1
        

def read_data(i):
    m = np.load('sinusoidal_current_npys/m_%d.npy'%i)
    m.shape = (-1,3)
    my = m[:,0]
    m2 = np.load('square_wave_current_npys/m_%d.npy'%i)
    m2.shape = (-1,3)
    my2 = m2[:,0]

    i1 = np.argmin(np.abs(m[:,2]))
    i2 = np.argmin(np.abs(m2[:,2]))
    
    return (my, my2, np.arctan2(m[i1,1], m[i1,0]), np.arctan2(m2[i2,1], m2[i2,0]))

#fig_mpl, ax1 = plt.subplots(1,figsize=(8,2.6), facecolor='white')

fig = plt.figure(figsize=(6,3.6), facecolor='white')

ax1 = plt.subplot2grid((2,5), (0,0), rowspan=1, colspan=2)
ax2 = plt.subplot2grid((2,5), (0,2), rowspan=1, colspan=3)
ax3 = plt.subplot2grid((2,5), (1,0), rowspan=1, colspan=5)

xs = np.linspace(0.5,3999.5,4000) # the x vector
(m1, m2, theta1, theta2) = read_data(0)

an = np.linspace(0, 2*np.pi, 100)
ax1.plot(np.cos(an), np.sin(an), '-',color='k', dashes=(3,3))
rotate_p1, = ax1.plot([0,np.sin(theta1)],[0,np.cos(theta1)], '-', linewidth=1, color='chocolate')
rotate_p2, = ax1.plot([0,np.sin(theta1)],[0,np.cos(theta1)], '-', linewidth=1, color='steelblue')
ax1.set_xlim(-1.1,1.1)
ax1.set_ylim(-1.1,1.1)
ax1.set_aspect('equal')
ax1.get_yaxis().set_visible(False)
ax1.get_xaxis().set_visible(False)
ax1.axis('off')
#ax1.set_xlabel(r'DW tile angle')
ax1.text(-0.87, -1.5, 'DW tile angle', fontsize=9)
#ax1.set_title('Tilt angle')
ax1.arrow(0, 0, 0.5, 0, head_width=0.15, head_length=0.15, fc='darkred', ec='darkred')
ax1.arrow(0, 0, 0, 0.5, head_width=0.15, head_length=0.15, fc='darkred', ec='darkred')
ax1.text(0.5, -0.3, 'x', fontsize=9)
ax1.text(-0.3, 0.5, 'y', fontsize=9)

u_p1, = ax2.plot([0,0],[0,0], '-', linewidth=1, color='chocolate', label='$u_1$')
u_p2, = ax2.plot([0,0],[0,0], '-', linewidth=1, color='steelblue', label='$u_2$')
ax2.set_xlim(0,6)
#ax2.set_xticks([0,1,2,3,4])
#ax2.set_ylim(-0.2,1.2)
ax2.set_yticks([0, 1])
ax2.set_ylim([-0.3,1.3])
ax2.set_ylabel(r'$u/u_0$')
ax2.set_xlabel(r'Time (ns)')
#ax2.text(4.4, -0.65, 'Time (ns)', fontsize=9)
l1 = ax2.legend(loc='upper right', shadow=True, frameon=False,labelspacing=0, handletextpad=0.3)
custom_legend(l1)
#ax2.set_xlabel('Time (ns)',fontsize=8)


p1,= ax3.plot(xs,m1*1e4,'-', linewidth=0.8, color='chocolate', label='$m_x$ with $u_1$')   
p2,= ax3.plot(xs,m2*1e4,'-', linewidth=0.8, color='steelblue', label='$m_x$ with $u_2$')

ax3.set_xlabel('z/a')
ax3.set_ylabel('$m_x$ $[10^{-4}]$')
ax3.set_ylim(-2,4)
plt.yticks([-2, 0, 2, 4])
#plt.xticks([])
    
#l1 = plt.legend(loc=2, shadow=True, frameon=False)
#custom_legend(l1)
#plt.gca().add_artist(l1)
l2 = ax3.legend(loc='upper right', shadow=True, frameon=False,labelspacing=0, handletextpad=0.3)
custom_legend(l2)

plt.tight_layout()
#plt.subplots_adjust(left=0.12, bottom=0.15, top=0.98, hspace=0.39)
 
# ANIMATE WITH MOVIEPY (UPDATE THE CURVE FOR EACH t). MAKE A GIF.

def make_frame_mpl(t):
    t_ns = t*0.2
    ts1.append(t_ns)
    u1.append((1-np.cos(t_ns*np.pi/2.0))/2.0)
    ts2.append(t_ns)
    u2.append(varying_u(t_ns))

    if t_ns%1.0==0.0:
        ts2.append(t_ns)
        if u2[-1] == 0:
            u2.append(1)
        else:
            u2.append(0)
    
    (m1, m2, theta1, theta2) = read_data(int(t*10))
    p1.set_ydata(m1*1e4)
    p2.set_ydata(m2*1e4)
    rotate_p1.set_data([[0,np.sin(theta1)],[0,np.cos(theta1)]])
    rotate_p2.set_data([[0,np.sin(theta2)],[0,np.cos(theta2)]])

    u_p1.set_data([ts1, u1])
    u_p2.set_data([ts2, u2])
    #ax2.set_title('t=%0.2f ns'%(t_ns))
    return mplfig_to_npimage(fig) # RGB image of the figure
 
animation = mpy.VideoClip(make_frame_mpl, duration=duration)
animation.write_gif("I.gif", fps=10)
