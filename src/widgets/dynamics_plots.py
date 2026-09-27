from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class DynamicsPlot(FigureCanvas):
    def __init__(self, kind):
        self.kind = kind
        self.figure = Figure(figsize=(7, 3.5), facecolor='#111820')
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(.10, .18, .97, .90)

    def _style(self):
        a = self.ax
        a.set_facecolor('#111820')
        a.tick_params(colors='#7d8b99', labelsize=8)
        for s in a.spines.values():
            s.set_color('#26313c')
        a.grid(True, color='#24303a', alpha=.65, lw=.7)

    def plot(self, df):
        a = self.ax
        a.clear()
        self._style()

        if self.kind == 'gg':
            a.scatter(df.ax_g, df.ay_g, c=df.speed_kmh, s=5, cmap='turbo', alpha=.55)
            a.set_title('G-G friction circle', color='#e6edf3', loc='left', fontsize=11, fontweight='bold')
            a.set_xlabel('Ax [g]', color='#6f7d8b', fontsize=8)
            a.set_ylabel('Ay [g]', color='#6f7d8b', fontsize=8)
            a.axhline(0, color='#3a4650', lw=.7)
            a.axvline(0, color='#3a4650', lw=.7)

        elif self.kind == 'understeer':
            a.scatter(df.ay_g, df.understeer_gradient_deg_per_g,
                      c=df.speed_kmh, s=5, cmap='viridis', alpha=.45)
            a.set_title('Understeer / oversteer gradient', color='#e6edf3', loc='left', fontsize=11, fontweight='bold')
            a.set_xlabel('Ay [g]', color='#6f7d8b', fontsize=8)
            a.set_ylabel('K [deg/g]', color='#6f7d8b', fontsize=8)
            a.axhline(0, color='#d0d7de', lw=.7, ls='--')

        elif self.kind == 'slip':
            for c, label in [('fl','FL'), ('fr','FR'), ('rl','RL'), ('rr','RR')]:
                a.plot(df.lap_time_s, df[f'slip_ratio_{c}'] * 100, lw=1.1, label=label)
            a.set_title('Tyre slip ratio', color='#e6edf3', loc='left', fontsize=11, fontweight='bold')
            a.set_xlabel('Lap time [s]', color='#6f7d8b', fontsize=8)
            a.set_ylabel('Slip [%]', color='#6f7d8b', fontsize=8)
            leg = a.legend(frameon=False, fontsize=7, ncol=4)
            for x in leg.get_texts():
                x.set_color('#9aa8b6')

        elif self.kind == 'friction':
            a.plot(df.lap_time_s, df.friction_utilization, lw=1.2)
            a.axhline(1, color='#d0d7de', lw=.8, ls='--')
            a.set_title('Friction utilization', color='#e6edf3', loc='left', fontsize=11, fontweight='bold')
            a.set_xlabel('Lap time [s]', color='#6f7d8b', fontsize=8)
            a.set_ylabel('sqrt(Ax² + Ay²) / (μg)', color='#6f7d8b', fontsize=8)

        self.figure.canvas.draw_idle()

    def save_png(self, path):
        self.figure.savefig(path, dpi=220, facecolor=self.figure.get_facecolor(), bbox_inches='tight')
