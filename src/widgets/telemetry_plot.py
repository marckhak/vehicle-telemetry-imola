from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class TelemetryPlot(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(7, 3.3), facecolor='#111820')
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(.07, .16, .98, .90)

    def plot(self, df, metric, title, ylabel):
        self.metric = metric
        self.title = title
        self.ax.clear()
        self.ax.set_facecolor('#111820')
        self.ax.tick_params(colors='#7d8b99', labelsize=8)
        for s in self.ax.spines.values():
            s.set_color('#26313c')
        self.ax.grid(True, color='#24303a', alpha=.65, lw=.7)
        self.ax.set_title(title, loc='left', color='#e6edf3', fontsize=11, fontweight='bold')
        self.ax.set_xlabel('Lap time [s]', color='#6f7d8b', fontsize=8)
        self.ax.set_ylabel(ylabel, color='#6f7d8b', fontsize=8)
        for lap, g in df.groupby('lap'):
            self.ax.plot(g.lap_time_s, g[metric], lw=1.4, alpha=.65, label=f'Lap {int(lap)}')
        leg = self.ax.legend(frameon=False, fontsize=8, ncol=min(5, df.lap.nunique()))
        for x in leg.get_texts():
            x.set_color('#9aa8b6')
        self.figure.canvas.draw_idle()

    def save_png(self, path):
        self.figure.savefig(path, dpi=220, facecolor=self.figure.get_facecolor(), bbox_inches='tight')
