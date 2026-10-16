from rocketpy import Accelerometer
from ..constants import g

adxl375_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=200 * g,              # 1961.3 m/s^2
    resolution=49e-3 * g,                   # 49 mg/LSB (20.5 LSB/g)
    noise_density=5e-3 * g,                 # 5 mg/sqrt(Hz)
    constant_bias=0.3 * g,                  # approx. representative 0g offset for this
                                              # "low precision" shock sensor, see note
    consider_gravity=False,
    name="ADXL375 Accelerometer",
)

bmi323_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=8 * g,                # 78.45 m/s^2
    resolution=g / 4096,                    # 4096 LSB/g @ 8g -> 2.394e-3 m/s^2/LSB
    noise_density=180e-6 * g,               # 180 ug/sqrt(Hz) -> 1.765e-3 m/s^2/sqrt(Hz)
    constant_bias=0.035 * g,                # +-35 mg typ. zero-g offset (soldered)
    temperature_bias=0.0003 * g,            # +-0.3 mg/K TCO
    consider_gravity=False,
    name="BMI323 Accelerometer",
)

lsm6dso32_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=32 * g,               # 313.8 m/s^2
    resolution=0.976e-3 * g,                # 0.976 mg/LSB @ 32g
    noise_density=70e-6 * g,                # 70 ug/sqrt(Hz) (AN5192, high-perf mode)
    constant_bias=0.040 * g,                # +-40 mg typ. zero-g level (approx., see note)
    temperature_bias=0.0005 * g,            # approx., not separately published for 32g variant
    consider_gravity=False,
    name="LSM6DSO32 Accelerometer",
)

truth_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    consider_gravity=False,
    name="LSM6DSO32 Accelerometer",
)