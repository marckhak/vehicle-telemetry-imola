from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np,pandas as pd
from .imola import TRACK_LENGTH_M,centerline,sector_at
from .vehicle_model import PARAMS
@dataclass
class SessionConfig:
 laps:int=5; hz:int=20; lap_time_s:float=98.; seed:int=42
def curvature_profile(s):
 x=s/TRACK_LENGTH_M;k=np.zeros_like(x)
 for a,b,val in [(.025,.065,.010),(.078,.115,-.012),(.180,.220,.009),(.230,.275,-.010),(.325,.370,.008),(.395,.455,-.011),(.465,.510,.009),(.525,.575,-.013),(.625,.690,.012)]:
  m=(x>=a)&(x<=b);u=(x[m]-a)/(b-a);k[m]+=val*np.sin(np.pi*u)**2
 return k
def speed_profile(s,rng):
 x=s/TRACK_LENGTH_M;v=255+22*np.sin(2*np.pi*(x+.12))+10*np.sin(6*np.pi*x)
 for a,b,f in [(.030,.060,.62),(.082,.115,.55),(.185,.215,.72),(.235,.270,.66),(.330,.365,.68),(.405,.455,.58),(.475,.505,.64),(.535,.570,.55),(.635,.685,.62)]:
  m=(x>=a)&(x<=b);u=(x[m]-a)/(b-a);v[m]*=(1-(1-f)*np.sin(np.pi*u)**2)
 return np.clip(v+rng.normal(0,2,len(s)),55,310)
def generate_session(config=SessionConfig()):
 rng=np.random.default_rng(config.seed);dt=1/config.hz;c=centerline(max(2400,int(config.lap_time_s*config.hz)));rows=[]
 for lap in range(1,config.laps+1):
  n=int(config.lap_time_s*config.hz);t=np.arange(n)*dt;frac=t/config.lap_time_s;s=frac*TRACK_LENGTH_M;pace={1:.975,2:.992,3:1.010,4:.985,5:.965}.get(lap,.98);vx=speed_profile(s,rng)*pace/3.6;k=curvature_profile(s);yaw=k*vx;ay=vx*yaw;ax=np.gradient(vx,dt)
  throttle=np.clip(58+35*np.tanh(ax/2.3)+rng.normal(0,4.5,n),0,100);brake=np.clip(-ax*18+rng.normal(0,2.5,n),0,100);steer=np.rad2deg(np.arctan(PARAMS.wheelbase_m*k)+np.deg2rad(PARAMS.understeer_deg_per_g)*(ay/9.80665))+rng.normal(0,.25,n)
  rpm=np.clip(3300+vx*72+throttle*16-brake*12,2500,11200);base=vx/(2*np.pi*PARAMS.wheel_radius_m)*60;rear=np.clip((throttle-55)/900, -.01,.085)-np.clip(brake/1500,0,.08)+rng.normal(0,.004,n);front=-np.clip(brake/1500,0,.08)+rng.normal(0,.003,n)
  wheels=[base*(1+front),base*(1+front),base*(1+rear),base*(1+rear)];voltage=400+2*np.sin(t/5)+rng.normal(0,.8,n);current=np.clip(22+throttle*1.55+np.maximum(ax,0)*20,8,235);power=voltage*current/1000;temp=70+.06*power+2*np.sin(t/8)+rng.normal(0,.7,n);soc=np.clip(96-np.cumsum(np.maximum(power,0))*dt/(config.laps*config.lap_time_s*1.65),0,100);gear=np.clip(np.floor(vx*3.6/32).astype(int),2,8);fault=np.full(n,'',object)
  if lap==2:m=(t>60)&(t<63);temp[m]+=24;fault[m]='HIGH_TEMPERATURE'
  if lap==3:m=(t>45)&(t<48);current[m]+=55;fault[m]='OVERCURRENT'
  if lap==4:m=(t>72)&(t<75);voltage[m]-=42;fault[m]='LOW_VOLTAGE'
  if lap==5:m=(t>30)&(t<32);vx[m]=np.nan;rpm[m]=np.nan;temp[m]=np.nan;[w.__setitem__(m,np.nan) for w in wheels];fault[m]='SENSOR_DROPOUT'
  idx=np.minimum((frac*(len(c)-1)).astype(int),len(c)-1);xs=c.iloc[idx].x_m.to_numpy();ys=c.iloc[idx].y_m.to_numpy()
  for i in range(n):
   rows.append(dict(timestamp_s=round((lap-1)*config.lap_time_s+t[i],3),lap=lap,lap_time_s=round(t[i],3),distance_m=round(float(s[i]),3),x_m=round(float(xs[i]),3),y_m=round(float(ys[i]),3),sector=sector_at(float(s[i])),speed_kmh=None if np.isnan(vx[i]) else round(float(vx[i]*3.6),3),rpm=None if np.isnan(rpm[i]) else round(float(rpm[i]),1),throttle_pct=round(float(throttle[i]),2),brake_pct=round(float(brake[i]),2),steering_deg=round(float(steer[i]),3),yaw_rate_dps=round(float(np.rad2deg(yaw[i])),4),voltage_v=round(float(voltage[i]),2),current_a=round(float(current[i]),2),power_kw=round(float(power[i]),2),motor_temp_c=None if np.isnan(temp[i]) else round(float(temp[i]),2),soc_pct=round(float(soc[i]),2),gear=int(gear[i]),wheel_speed_fl_rpm=None if np.isnan(wheels[0][i]) else round(float(wheels[0][i]),2),wheel_speed_fr_rpm=None if np.isnan(wheels[1][i]) else round(float(wheels[1][i]),2),wheel_speed_rl_rpm=None if np.isnan(wheels[2][i]) else round(float(wheels[2][i]),2),wheel_speed_rr_rpm=None if np.isnan(wheels[3][i]) else round(float(wheels[3][i]),2),fault=fault[i]))
 return pd.DataFrame(rows)
def save_session(path='data/simulated/imola_telemetry.csv',config=SessionConfig()):
 df=generate_session(config);Path(path).parent.mkdir(parents=True,exist_ok=True);df.to_csv(path,index=False);return df
if __name__=='__main__': print(f'Generated {len(save_session()):,} samples')
