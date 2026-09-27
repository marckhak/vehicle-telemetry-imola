from dataclasses import dataclass
G=9.80665
@dataclass(frozen=True)
class VehicleParams:
 mass_kg:float=650.0
 wheelbase_m:float=2.95
 cg_height_m:float=.30
 wheel_radius_m:float=.33
 frontal_area_m2:float=1.65
 air_density_kgpm3:float=1.225
 aero_downforce_coeff:float=2.0
 tyre_mu:float=1.75
 understeer_deg_per_g:float=1.8
 battery_energy_kwh:float=7.5
PARAMS=VehicleParams()
def aero_downforce(v): return .5*PARAMS.air_density_kgpm3*PARAMS.aero_downforce_coeff*PARAMS.frontal_area_m2*v*v
def wheel_load_distribution(v,ax):
 transfer=PARAMS.mass_kg*ax*PARAMS.cg_height_m/PARAMS.wheelbase_m
 return max(PARAMS.mass_kg*G/2-transfer/2,1),max(PARAMS.mass_kg*G/2+transfer/2,1)
