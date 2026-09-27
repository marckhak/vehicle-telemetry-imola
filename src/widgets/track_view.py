from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import LineCollection
from matplotlib import cm, colors
from ..imola import centerline, CORNERS

class TrackView(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(7, 4.5), facecolor='#111820')
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self._base()

    def _base(self):
        self.ax.clear()
        self.ax.set_facecolor('#111820')
        c = centerline()
        self.ax.plot(c.x_m, c.y_m, color='#34414d', lw=10)
        self.ax.plot(c.x_m, c.y_m, color='#e8edf2', lw=5)
        self.ax.plot(c.x_m, c.y_m, color='#202932', lw=3)
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        for n, f, _ in CORNERS:
            i = int(f * (len(c) - 1))
            x, y = c.iloc[i][['x_m', 'y_m']]
            self.ax.text(x, y, str(n), ha='center', va='center', fontsize=8, color='#111820',
                         fontweight='bold', bbox=dict(boxstyle='circle,pad=.25', fc='white', ec='#d7dde2'))

    def set_data(self, df):
        self._base()
        v = df.dropna(subset=['x_m', 'y_m', 'speed_kmh'])
        p = v[['x_m', 'y_m']].to_numpy()
        seg = __import__('numpy').stack([p[:-1], p[1:]], axis=1)
        lc = LineCollection(seg, cmap=cm.turbo,
                            norm=colors.Normalize(vmin=v.speed_kmh.min(), vmax=v.speed_kmh.max()))
        lc.set_array(v.speed_kmh.to_numpy()[:-1])
        lc.set_linewidth(3)
        self.ax.add_collection(lc)
        self.figure.canvas.draw_idle()

    def save_png(self, path):
        self.figure.savefig(path, dpi=220, facecolor=self.figure.get_facecolor(), bbox_inches='tight')
