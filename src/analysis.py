import pandas as pd
def lap_summary(df):
 rows=[]
 for lap,g in df.groupby('lap'):
  rows.append({'Lap':int(lap),'Lap time [s]':g.lap_time_s.max(),'Max speed [km/h]':g.speed_kmh.max(),'Max Ay [g]':g.ay_g.max(),'Max Ax [g]':g.ax_g.max(),'Max RPM':g.rpm.max(),'Max temp [°C]':g.motor_temp_c.max(),'Avg power [kW]':g.power_kw.mean()})
 return pd.DataFrame(rows).round(3)
def fault_summary(df):
 f=df[df.fault.fillna('')!=''];rows=[]
 for (fault,lap),g in f.groupby(['fault','lap']):rows.append({'Fault':fault,'Lap':int(lap),'Start [s]':g.lap_time_s.min(),'End [s]':g.lap_time_s.max(),'Samples':len(g)})
 return pd.DataFrame(rows).round(3)
def session_metrics(df):return dict(laps=int(df.lap.nunique()),max_speed=float(df.speed_kmh.max()),max_rpm=float(df.rpm.max()),max_temp=float(df.motor_temp_c.max()),avg_power=float(df.power_kw.mean()),faults=int((df.fault.fillna('')!='').sum()))
