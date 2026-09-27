import unittest
from src.imola import centerline,TRACK_LENGTH_M
class TestImola(unittest.TestCase):
    def test_length(self): self.assertAlmostEqual(centerline().distance_m.iloc[-1],TRACK_LENGTH_M,delta=1)
if __name__=='__main__': unittest.main()
