from matplotlib import use as mpluse
mpluse("Agg") 
from matplotlib.backends import backend_agg as agg 
from pylab import figure
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
from numpy import linspace

baseLocations = {
    "x" : [-5, -5, 21, 21],
    "y" : [-5, 25, -5, 25],
    "z" : [0, 0, 0, 0]
}
types = {
    1 : "Light",
    2 : "Heat",
}

def makeGridData(sensors, focus="Heat"):
    xl, yl, zl = [], [], []
    for key, sensor in sensors.iteritems():
        locx, locy = sensor.position
        if locx < 0 or locy < 0:
            continue
        if types[sensor.type] != focus:
            continue
        locx = locx/25.0
        locy = locy/25.0
        xl.append(locx)
        yl.append(locy)
        zl.append(sensor.values[-1])
    x = baseLocations["x"] + xl
    y = baseLocations["y"] + yl
    z = baseLocations["z"] + zl
    xi = linspace(0, 16, 400)
    yi = linspace(0, 20, 500)
    zi = griddata(x, y, z, xi, yi, interp='linear')
    return xi, yi, zi

def getMapData(sensors, size):
    size = [size[0]/100, size[1]/100]
    fig = figure(figsize=size, dpi=100, frameon=False)
    ax = fig.gca()
    ax.invert_yaxis()
    ax.axis('off')
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    fig.tight_layout(pad=0)

    xi, yi, zi = makeGridData(sensors)
    levels = [n*50 for n in range(21)]
    ax.contourf(xi, yi, zi, levels, cmap='CMRmap')
     
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    data = canvas.get_renderer().tostring_rgb()
    plt.close('all')
    return data

