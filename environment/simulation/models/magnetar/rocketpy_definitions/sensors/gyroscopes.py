from rocketpy import Gyroscope
from ..constants import g
import numpy as np

bmi323_gyro = Gyroscope(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=np.radians(2000),      # 34.91 rad/s
    resolution=np.radians(1 / 16.4),         # 16.4 LSB/dps @ 2000dps -> 1.064e-3 rad/s/LSB
    noise_density=np.radians(0.007),         # 0.007 dps/sqrt(Hz) -> 1.222e-4 rad/s/sqrt(Hz)
    constant_bias=np.radians(1.0),           # +-1 dps typ. zero-rate offset (lifetime)
    temperature_bias=np.radians(0.04),       # +-0.04 dps/K TCO
    name="BMI323 Gyroscope",
)

lsm6dso32_gyro = Gyroscope(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=np.radians(2000),      # 34.91 rad/s
    resolution=np.radians(70e-3),            # 70 mdps/LSB @ 2000dps
    noise_density=np.radians(3.8e-3),        # 3.8 mdps/sqrt(Hz) (AN5192)
    constant_bias=np.radians(0.5),           # +-0.5 dps typ. zero-rate level
    temperature_bias=np.radians(0.05),       # approx., see note
    name="LSM6DSO32 Gyroscope",
)

truth_gyro = Gyroscope(
    sampling_rate=200,
    orientation=(0, 0, 0),
    name="LSM6DSO32 Gyroscope",
)