from __future__ import annotations
import numpy as np,pandas as pd
from .vehicle_model import PARAMS,G
def add_calculated_channels(df,params=PARAMS):
 out=df.copy();t=out.timestamp_s.to_numpy(float);vx=out.speed_kmh.to_numpy(float)/3.6;yaw=np.deg2rad(out.yaw_rate_dps.to_numpy(float));out['ax_mps2']=np.gradient(vx,t);out['ay_mps2']=vx*yaw;out['ax_g']=out.ax_mps2/G;out['ay_g']=out.ay_mps2/G;out['curvature_1pm']=np.divide(yaw,vx,out=np.full_like(vx,np.nan),where=np.abs(vx)>1)
 sk=np.arctan(params.wheelbase_m*out.curvature_1pm.to_numpy(float));out['steering_kin_deg']=np.rad2deg(sk);lg=out.ay_g.to_numpy(float);d=np.deg2rad(out.steering_deg.to_numpy(float));valid=(np.abs(lg)>.15)&(vx>12)&np.isfinite(d)&np.isfinite(sk);kus=np.full(len(out),np.nan);kus[valid]=np.rad2deg((d[valid]-sk[valid])/lg[valid]);out['understeer_gradient_deg_per_g']=pd.Series(kus).rolling(15,min_periods=1,center=True).median().to_numpy()
 for name in ['fl','fr','rl','rr']:
  wrpm=out[f'wheel_speed_{name}_rpm'].to_numpy(float);wv=wrpm*2*np.pi*params.wheel_radius_m/60;out[f'slip_ratio_{name}']=(wv-vx)/np.maximum(np.abs(vx),1);out.loc[~np.isfinite(vx),f'slip_ratio_{name}']=np.nan
 out['friction_utilization']=np.sqrt(out.ax_g**2+out.ay_g**2)/params.tyre_mu
 return out
def dynamics_metrics(df):
 k=df.understeer_gradient_deg_per_g.dropna();return dict(max_ay=float(df.ay_g.max()),max_ax=float(df.ax_g.max()),min_ax=float(df.ax_g.min()),median_kus=float(k.median()) if len(k) else np.nan,max_rear_slip_pct=float(max(df.slip_ratio_rl.abs().max(),df.slip_ratio_rr.abs().max())*100),max_util=float(df.friction_utilization.max()))
def slip_summary(df):
 rows=[]
 for w in ['fl','fr','rl','rr']:
  s=df[f'slip_ratio_{w}'].dropna();rows.append({'Wheel':w.upper(),'Mean [%]':s.mean()*100,'Max [%]':s.max()*100,'Min [%]':s.min()*100,'95th |slip| [%]':s.abs().quantile(.95)*100})
 return pd.DataFrame(rows)
