import unittest,numpy as np,pandas as pd
from src.dynamics import add_calculated_channels
class TestDynamics(unittest.TestCase):
    def test_channels_and_slip(self):
        n=100;t=np.arange(n)*.05;v=np.full(n,100.)
        df=pd.DataFrame({'timestamp_s':t,'speed_kmh':v,'yaw_rate_dps':np.full(n,10.),'steering_deg':np.full(n,3.),'wheel_speed_fl_rpm':np.full(n,800.),'wheel_speed_fr_rpm':np.full(n,800.),'wheel_speed_rl_rpm':np.full(n,820.),'wheel_speed_rr_rpm':np.full(n,820.)})
        o=add_calculated_channels(df); self.assertGreater(o.ay_g.mean(),0); self.assertGreater(o.slip_ratio_rl.mean(),o.slip_ratio_fl.mean())
if __name__=='__main__': unittest.main()
