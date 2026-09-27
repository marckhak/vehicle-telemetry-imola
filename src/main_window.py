from pathlib import Path
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from .theme import APP_QSS
from .telemetry import SessionConfig, save_session
from .dynamics import add_calculated_channels, dynamics_metrics, slip_summary
from .analysis import lap_summary, fault_summary
from .widgets.track_view import TrackView
from .widgets.telemetry_plot import TelemetryPlot
from .widgets.dynamics_plots import DynamicsPlot

BASE=Path(__file__).resolve().parent.parent
DATA=BASE/'data/simulated/imola_telemetry.csv'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Vehicle Telemetry — Imola Dynamics'); self.resize(1450,900)
        self.setStyleSheet(APP_QSS); self.df=None
        self.pages=QStackedWidget(); self.track=TrackView(); self.ps=TelemetryPlot(); self.pr=TelemetryPlot(); self.pp=TelemetryPlot(); self.pt=TelemetryPlot(); self.dgg=DynamicsPlot('gg'); self.dus=DynamicsPlot('understeer'); self.dslip=DynamicsPlot('slip'); self.dfric=DynamicsPlot('friction')
        self._build(); self._load()
    def panel(self, title, widget=None, export_name=None):
        f=QFrame(objectName='panel'); l=QVBoxLayout(f); l.setContentsMargins(12,10,12,12)
        header=QHBoxLayout(); header.addWidget(QLabel(title,objectName='panelTitle')); header.addStretch()
        if widget is not None and export_name:
            b=QPushButton('↗ PNG',objectName='export'); b.setToolTip('Esporta questo grafico come PNG'); b.setFixedHeight(27); b.setMinimumWidth(68)
            b.clicked.connect(lambda _, w=widget, n=export_name: self.export_chart(w,n)); header.addWidget(b)
        l.addLayout(header)
        if widget is not None: l.addWidget(widget)
        return f,l

    def export_chart(self, widget, default_name):
        if self.df is None: return
        path,_=QFileDialog.getSaveFileName(self,'Esporta grafico',default_name,'PNG image (*.png)')
        if path:
            try: widget.save_png(path)
            except Exception as e: QMessageBox.critical(self,'Export error',str(e))

    def _build(self):
        root=QWidget(); self.setCentralWidget(root); lay=QHBoxLayout(root); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        side=QFrame(objectName='sidebar'); side.setFixedWidth(225); sl=QVBoxLayout(side); sl.setContentsMargins(16,20,16,16)
        sl.addWidget(QLabel('VEHICLE\nTELEMETRY',objectName='brand')); sl.addWidget(QLabel('IMOLA DYNAMICS TOOL',objectName='subtitle')); sl.addSpacing(20)
        self.nav=[]
        for i,name in enumerate(['Overview','Telemetry','Vehicle Dynamics','Lap Analysis','Faults']):
            b=QPushButton(name,objectName='nav'); b.setCheckable(True); b.clicked.connect(lambda _,i=i:self.page(i)); self.nav.append(b); sl.addWidget(b)
        self.nav[0].setChecked(True); sl.addSpacing(20); sl.addWidget(QLabel('SIMULATION',objectName='section'))
        sl.addWidget(QLabel('Laps',objectName='subtitle')); self.laps=QSpinBox(); self.laps.setRange(1,20); self.laps.setValue(5); sl.addWidget(self.laps)
        b=QPushButton('Generate session',objectName='primary'); b.clicked.connect(self.generate); sl.addWidget(b)
        b=QPushButton('Import normalized CSV'); b.clicked.connect(self.import_csv); sl.addWidget(b)
        b=QPushButton('Export analyzed CSV'); b.clicked.connect(self.export_csv); sl.addWidget(b)
        sl.addStretch(); sl.addWidget(QLabel('Imola • 4.909 km',objectName='subtitle')); lay.addWidget(side); lay.addWidget(self.pages,1)
        self.pages.addWidget(self.overview()); self.pages.addWidget(self.telemetry()); self.pages.addWidget(self.dynamics()); self.pages.addWidget(self.laps_page()); self.pages.addWidget(self.fault_page())

    def page(self,i):
        self.pages.setCurrentIndex(i)
        for j,b in enumerate(self.nav): b.setChecked(j==i)

    def overview(self):
        w=QWidget(); l=QVBoxLayout(w); h=QLabel('Session Overview'); h.setStyleSheet('font-size:24px;font-weight:700;color:#fff'); l.addWidget(h)
        row=QHBoxLayout(); self.cards=[]
        for title,unit in [('LAPS',''),('MAX SPEED','km/h'),('MAX AY','g'),('K US','deg/g'),('MAX SLIP','%')]:
            f=QFrame(objectName='card'); x=QVBoxLayout(f); x.addWidget(QLabel(title,objectName='cardTitle')); v=QLabel('—',objectName='cardValue'); x.addWidget(v); x.addWidget(QLabel(unit,objectName='cardUnit')); self.cards.append(v); row.addWidget(f)
        l.addLayout(row); split=QSplitter(Qt.Horizontal)
        p,pl=self.panel('TRACK / SPEED TRACE',self.track,'imola_track_speed.png'); split.addWidget(p)
        p,pl=self.panel('ENGINEERING SUMMARY'); self.summary=QLabel(); self.summary.setWordWrap(True); pl.addWidget(self.summary); split.addWidget(p); l.addWidget(split,1); return w

    def telemetry(self):
        w = QWidget()
        grid = QGridLayout(w)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(12)

        panels = [
            (0, 0, self.ps, "Vehicle speed", "speed_kmh", "km/h"),
            (0, 1, self.pr, "RPM", "rpm", "rpm"),
            (1, 0, self.pp, "Electrical power", "power_kw", "kW"),
            (1, 1, self.pt, "Motor temperature", "motor_temp_c", "°C"),
        ]

        for row, col, plot, title, metric, ylabel in panels:
            panel, layout = self.panel(title)
            layout.addWidget(plot)
            grid.addWidget(panel, row, col)

        return w

    def dynamics(self):
        w=QWidget(); l=QGridLayout(w)
        charts=[((0,0),self.dgg,'G-G friction circle','gg_friction_circle.png'),((0,1),self.dus,'Understeer / oversteer gradient','understeer_gradient.png'),((1,0),self.dslip,'Tyre slip ratio','tyre_slip_ratio.png'),((1,1),self.dfric,'Friction utilization','friction_utilization.png')]
        for pos,plot,title,name in charts:
            p,pl=self.panel(title,plot,name); l.addWidget(p,*pos)
        return w

    def laps_page(self):
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel('Lap Analysis')); p,pl=self.panel('LAP PERFORMANCE'); self.lt=QTableWidget(); pl.addWidget(self.lt); l.addWidget(p); p,pl=self.panel('TYRE SLIP SUMMARY'); self.st=QTableWidget(); pl.addWidget(self.st); l.addWidget(p); return w
    def fault_page(self):
        w=QWidget(); l=QVBoxLayout(w); l.addWidget(QLabel('Fault Monitor')); p,pl=self.panel('DETECTED EVENTS'); self.ft=QTableWidget(); pl.addWidget(self.ft); l.addWidget(p); return w
    def _load(self):
        if not DATA.exists(): self.generate()
        else: self.df=add_calculated_channels(pd.read_csv(DATA)); self.refresh()
    def generate(self):
        raw=save_session(str(DATA),SessionConfig(laps=self.laps.value())); self.df=add_calculated_channels(raw); self.refresh()
    def refresh(self):
        if self.df is None:return
        m=dynamics_metrics(self.df)
        for lab,val in zip(self.cards,[str(self.df.lap.nunique()),f'{self.df.speed_kmh.max():.0f}',f'{m["max_ay"]:.2f}',f'{m["median_kus"]:.2f}',f'{m["max_rear_slip_pct"]:.1f}']): lab.setText(val)
        self.summary.setText(f'Samples: {len(self.df):,}\n\nPeak Ay: {m["max_ay"]:.2f} g\n\nMedian KUS: {m["median_kus"]:.2f} deg/g\n\nPeak rear slip: {m["max_rear_slip_pct"]:.1f}%')
        self.track.set_data(self.df); self.ps.plot(self.df,'speed_kmh','Vehicle speed','km/h'); self.pr.plot(self.df,'rpm','RPM','rpm'); self.pp.plot(self.df,'power_kw','Electrical power','kW'); self.pt.plot(self.df,'motor_temp_c','Motor temperature','°C'); self.dgg.plot(self.df); self.dus.plot(self.df); self.dslip.plot(self.df); self.dfric.plot(self.df)
        self.fill(self.lt,lap_summary(self.df)); self.fill(self.st,slip_summary(self.df)); self.fill(self.ft,fault_summary(self.df))
    def fill(self,t,df):
        t.clear(); t.setRowCount(len(df)); t.setColumnCount(len(df.columns)); t.setHorizontalHeaderLabels(list(df.columns));
        for r,(_,row) in enumerate(df.iterrows()):
            for c,v in enumerate(row): t.setItem(r,c,QTableWidgetItem(str(v)))
        t.resizeColumnsToContents()
    def import_csv(self):
        path,_=QFileDialog.getOpenFileName(self,'Import telemetry','','CSV (*.csv)')
        if not path:return
        try: self.df=add_calculated_channels(pd.read_csv(path)); self.refresh()
        except Exception as e: QMessageBox.critical(self,'Import error',str(e))
    def export_csv(self):
        if self.df is None:return
        path,_=QFileDialog.getSaveFileName(self,'Export analyzed telemetry','imola_analyzed.csv','CSV (*.csv)')
        if path:self.df.to_csv(path,index=False)
