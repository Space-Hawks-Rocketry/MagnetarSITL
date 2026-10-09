

# Need to come up with a better name for this file;

import numpy as np

from rocketpy import Accelerometer, Gyroscope, Barometer, GnssReceiver
from magnetometer import Magnetometer
from environments.env import env

# Magic Number
G0 = 9.80665

# ============================================================================
# 5. SENSORS
# ============================================================================
# All sensors are mounted in a notional avionics bay ~0.3 m ahead of the dry
# CG, aligned with the body axes (default orientation).
AV_BAY_POSITION = 0.3

# ---- IMU #1: Bosch BMI323 -- low-g (8 g), high precision --------------------
# Source: Bosch BMI323 datasheet (bst-bmi323-ds000), accelerometer @ FS=8g,
# gyroscope @ FS=2000 dps.
bmi323_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=8 * G0,                # 78.45 m/s^2
    resolution=G0 / 4096,                    # 4096 LSB/g @ 8g -> 2.394e-3 m/s^2/LSB
    noise_density=180e-6 * G0,               # 180 ug/sqrt(Hz) -> 1.765e-3 m/s^2/sqrt(Hz)
    constant_bias=0.035 * G0,                # +-35 mg typ. zero-g offset (soldered)
    temperature_bias=0.0003 * G0,            # +-0.3 mg/K TCO
    consider_gravity=False,
    name="BMI323 Accelerometer",
)
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

# ---- IMU #2: STM LSM6DSO32 -- general reference (32 g) ---------------------
# Source: ST LSM6DSO32 datasheet + AN5192 (shared silicon w/ LSM6DSO, same
# noise densities); accelerometer @ FS=32g, gyroscope @ FS=2000 dps.
lsm6dso32_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=32 * G0,               # 313.8 m/s^2
    resolution=0.976e-3 * G0,                # 0.976 mg/LSB @ 32g
    noise_density=70e-6 * G0,                # 70 ug/sqrt(Hz) (AN5192, high-perf mode)
    constant_bias=0.040 * G0,                # +-40 mg typ. zero-g level (approx., see note)
    temperature_bias=0.0005 * G0,            # approx., not separately published for 32g variant
    consider_gravity=False,
    name="LSM6DSO32 Accelerometer",
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

# ---- IMU #3: Analog Devices ADXL375 -- high-g (200 g), accel only ----------
# Source: ADXL375 datasheet (Rev. B) + ADI EngineerZone application note.
adxl375_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=200 * G0,              # 1961.3 m/s^2
    resolution=49e-3 * G0,                   # 49 mg/LSB (20.5 LSB/g)
    noise_density=5e-3 * G0,                 # 5 mg/sqrt(Hz)
    constant_bias=0.3 * G0,                  # approx. representative 0g offset for this
                                              # "low precision" shock sensor, see note
    consider_gravity=False,
    name="ADXL375 Accelerometer",
)

# ---- Barometer #1: Bosch BMP581 --------------------------------------------
# Source: Bosch BMP581 datasheet + Bosch press release (relative accuracy
# +-6 Pa / +-0.5 m, RMS noise 0.08 Pa, resolution 1/64 Pa, TCO 0.5 Pa/K).
bmp581_baro = Barometer(
    sampling_rate=50,
    measurement_range=125000,                # Pa, sensor's full operating range is 30-125 kPa
    resolution=1 / 64,                       # Pa/LSB
    noise_density=0.08,                      # Pa/sqrt(Hz) (approx., see note)
    temperature_bias=0.5,                    # Pa/K TCO
    name="BMP581",
)

# ---- Barometer #2: Bosch BMP390 --------------------------------------------
# Source: Bosch BMP390 datasheet (relative accuracy +-3 Pa / +-0.25 m).
bmp390_baro = Barometer(
    sampling_rate=50,
    measurement_range=125000,
    resolution=0.016,                        # Pa/LSB, approx.
    noise_density=0.03,                      # Pa/sqrt(Hz), approx., see note
    temperature_bias=0.75,                   # Pa/K TCO (resistive tech, higher than BMP581)
    name="BMP390",
)

# ---- Magnetometer #1: PNI RM3100 -- high precision -------------------------
# Source: PNI RM3100 datasheet (resolution/noise floor) + RM3100 user manual
# (linear range ~100,000 nT).
rm3100_mag = Magnetometer(
    sampling_rate=100,
    latitude=env.latitude,
    longitude=env.longitude,
    elevation=env.elevation,
    date=env.date,
    orientation=(0, 0, 0),
    measurement_range=80e-6,                 # +-80 uT, comfortably covers local field + noise
    resolution=13e-9,                        # 13 nT/LSB (given)
    noise_density=4e-15,                     # 4 pT/sqrt(Hz) (datasheet noise floor)
    constant_bias=50e-9,                     # small representative board-level offset
    name="RM3100",
)

# ---- Magnetometer #2: Bosch BMM150 -- general measurement ------------------
# Source: Bosch BMM150 datasheet (range +-1300/+-2500 uT, 0.3 uT resolution).
bmm150_mag = Magnetometer(
    sampling_rate=50,
    latitude=env.latitude,
    longitude=env.longitude,
    elevation=env.elevation,
    date=env.date,
    orientation=(0, 0, 0),
    measurement_range=1300e-6,               # +-1300 uT (uniform per-axis approx.; Z is +-2500 uT)
    resolution=0.3e-6,                       # 0.3 uT/LSB (given)
    noise_density=0.6e-6,                    # approx. self-noise, see note
    constant_bias=2e-6,                      # representative uncalibrated hard-iron-like offset
    name="BMM150",
)

max_f10s_gnss = GnssReceiver(
    sampling_rate=10,
    altitude_accuracy=1.5 * 2.0, # I'll assume that altitude accuracuy is twice as bad
    position_accuracy=1.5,
    name="Max-F10S"
)