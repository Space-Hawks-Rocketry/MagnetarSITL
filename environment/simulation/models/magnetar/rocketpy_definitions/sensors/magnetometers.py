from ...rocketpy_classes.magnetometer import Magnetometer
from ..environment import env

print("\nSTATUS: Computing geomagnetic model...")
geomagnetic_data = Magnetometer.computeGeomagneticData(
    env.elevation,
    env.longitude,
    env.latitude,
    env.date
)
print("STATUS: Completed geomagnetic model.")

bmm150_mag = Magnetometer(
    sampling_rate=50,
    geomagnetic_data=geomagnetic_data,
    orientation=(0, 0, 0),
    measurement_range=1300e-6,               # +-1300 uT (uniform per-axis approx.; Z is +-2500 uT)
    resolution=0.3e-6,                       # 0.3 uT/LSB (given)
    noise_density=0.6e-6,                    # approx. self-noise, see note
    constant_bias=2e-6,                      # representative uncalibrated hard-iron-like offset
    name="BMM150",
)

rm3100_mag = Magnetometer(
    sampling_rate=100,
    geomagnetic_data=geomagnetic_data,
    orientation=(0, 0, 0),
    measurement_range=80e-6,                 # +-80 uT, comfortably covers local field + noise
    resolution=13e-9,                        # 13 nT/LSB (given)
    noise_density=4e-15,                     # 4 pT/sqrt(Hz) (datasheet noise floor)
    constant_bias=50e-9,                     # small representative board-level offset
    name="RM3100",
)

truth_mag = Magnetometer(
    sampling_rate=100,
    geomagnetic_data=geomagnetic_data,
    orientation=(0, 0, 0),
    name="RM3100",
)

