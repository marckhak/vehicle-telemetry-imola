from __future__ import annotations
import numpy as np
import pandas as pd
TRACK_LENGTH_M=4909.0
CONTROL_POINTS=np.array([
[-1550,-520],[-1730,-430],[-1770,-180],[-1680,120],[-1480,350],[-1220,500],[-930,555],[-680,590],[-430,525],[-180,355],[80,190],[350,155],[560,145],[700,210],[720,430],[680,680],[540,835],[300,875],[20,860],[-250,825],[-410,650],[-385,410],[-300,230],[-380,125],[-650,120],[-920,100],[-1130,20],[-1280,-120],[-1420,-290],[-1600,-450],[-1700,-610],[-1630,-735],[-1400,-705],[-1120,-620],[-820,-560],[-500,-555],[-170,-570],[160,-590],[480,-595],[780,-560],[1040,-520],[1220,-470],[1310,-360],[1280,-250],[1160,-170],[1010,-190],[920,-330],[1030,-500],[1250,-635],[1500,-690],[1710,-650],[1810,-520],[1720,-420],[1530,-355],[1330,-330],[1160,-285],[1040,-190],[1000,-20],[1100,160],[1280,390],[1470,610],[1690,690],[1900,640],[2040,500],[2050,300],[1970,120],[1870,-40],[1740,-210],[1580,-360],[1410,-455],[1180,-510],[900,-520],[620,-520],[330,-530],[40,-530],[-260,-520],[-560,-510],[-850,-505],[-1120,-500],[-1350,-505],[-1550,-520]],dtype=float)
CORNERS=[(1,.030,'Variante Bassa'),(2,.080,'Tamburello'),(3,.092,'Tamburello'),(4,.105,'Tamburello'),(5,.190,'Villeneuve'),(6,.235,'Villeneuve'),(7,.285,'Tosa'),(8,.335,'Piratella'),(9,.365,'Piratella'),(10,.405,'Acque Minerali'),(11,.435,'Acque Minerali'),(12,.475,'Acque Minerali'),(13,.535,'Variante Alta'),(14,.548,'Variante Alta'),(15,.565,'Variante Alta'),(16,.640,'Rivazza'),(17,.655,'Rivazza'),(18,.670,'Rivazza'),(19,.705,'Curva 19')]
SECTORS=[(0,1/3,'S1'),(1/3,2/3,'S2'),(2/3,1,'S3')]
def _spline(points,samples=2400):
 p=np.vstack([points[-2:],points,points[:2]]); out=[]
 for i in range(1,len(points)+1):
  p0,p1,p2,p3=p[i-1:i+3]; n=max(8,samples//len(points)); t=np.linspace(0,1,n,endpoint=False); t2=t*t; t3=t2*t
  out.append(.5*((2*p1)+(-p0+p2)*t[:,None]+(2*p0-5*p1+4*p2-p3)*t2[:,None]+(-p0+3*p1-3*p2+p3)*t3[:,None]))
 return np.vstack(out)
def centerline(samples=2400):
 xy=_spline(CONTROL_POINTS,samples); xy=np.vstack([xy,xy[0]]); d=np.linalg.norm(np.diff(xy,axis=0),axis=1); xy*=TRACK_LENGTH_M/d.sum(); d=np.linalg.norm(np.diff(xy,axis=0),axis=1); s=np.r_[0,np.cumsum(d)]
 return pd.DataFrame({'x_m':xy[:,0],'y_m':xy[:,1],'distance_m':s})
def sector_at(distance_m):
 f=(distance_m%TRACK_LENGTH_M)/TRACK_LENGTH_M
 for a,b,n in SECTORS:
  if a<=f<b:return n
 return 'S3'
