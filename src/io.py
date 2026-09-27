import pandas as pd
REQUIRED=['timestamp_s','lap','lap_time_s','distance_m','x_m','y_m','sector','speed_kmh','rpm','throttle_pct','brake_pct','steering_deg','yaw_rate_dps','voltage_v','current_a','power_kw','motor_temp_c','soc_pct','gear','wheel_speed_fl_rpm','wheel_speed_fr_rpm','wheel_speed_rl_rpm','wheel_speed_rr_rpm','fault']
def validate_schema(df):return [c for c in REQUIRED if c not in df.columns]
def load_csv(path):
 df=pd.read_csv(path);m=validate_schema(df)
 if m:raise ValueError('Missing required telemetry columns: '+', '.join(m))
 return df
